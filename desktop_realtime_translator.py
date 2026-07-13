import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import numpy as np
import soundcard as sc
from deep_translator import GoogleTranslator
from faster_whisper import WhisperModel


class RealtimeTranslatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Desktop Realtime EN->ZH Translator")
        self.root.geometry("980x700")

        self.running = False
        self.worker_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.ui_queue: queue.Queue[tuple[str, str]] = queue.Queue()

        self.model: WhisperModel | None = None
        self.translator = GoogleTranslator(source="en", target="zh-TW")

        self.loopback_mics: list[sc.Microphone] = []
        self.selected_mic_index = tk.StringVar()
        self.model_size = tk.StringVar(value="small")
        self.chunk_seconds = tk.DoubleVar(value=3.0)
        self.status_text = tk.StringVar(value="Ready")

        self._build_ui()
        self._refresh_sources()
        self._schedule_ui_updates()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Audio Source (Loopback):").grid(row=0, column=0, sticky=tk.W)
        self.source_combo = ttk.Combobox(top, textvariable=self.selected_mic_index, state="readonly", width=70)
        self.source_combo.grid(row=0, column=1, sticky=tk.EW, padx=8)

        refresh_btn = ttk.Button(top, text="Refresh Sources", command=self._refresh_sources)
        refresh_btn.grid(row=0, column=2, padx=4)

        ttk.Label(top, text="Whisper Model:").grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        model_combo = ttk.Combobox(top, textvariable=self.model_size, state="readonly", width=20)
        model_combo["values"] = ["base", "small", "medium"]
        model_combo.grid(row=1, column=1, sticky=tk.W, padx=8, pady=(8, 0))

        ttk.Label(top, text="Chunk Seconds:").grid(row=1, column=1, sticky=tk.E, pady=(8, 0))
        chunk_spin = ttk.Spinbox(top, from_=1.5, to=8.0, increment=0.5, textvariable=self.chunk_seconds, width=8)
        chunk_spin.grid(row=1, column=2, sticky=tk.W, pady=(8, 0))

        controls = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        controls.pack(fill=tk.X)
        self.start_btn = ttk.Button(controls, text="Start", command=self.start)
        self.start_btn.pack(side=tk.LEFT)
        self.stop_btn = ttk.Button(controls, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=8)
        clear_btn = ttk.Button(controls, text="Clear", command=self.clear_text)
        clear_btn.pack(side=tk.LEFT)

        ttk.Label(controls, textvariable=self.status_text).pack(side=tk.RIGHT)

        panes = ttk.Panedwindow(self.root, orient=tk.VERTICAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        english_frame = ttk.Labelframe(panes, text="English Transcript")
        chinese_frame = ttk.Labelframe(panes, text="Chinese Translation")
        panes.add(english_frame, weight=1)
        panes.add(chinese_frame, weight=1)

        self.english_box = ScrolledText(english_frame, wrap=tk.WORD, height=14)
        self.english_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.chinese_box = ScrolledText(chinese_frame, wrap=tk.WORD, height=14)
        self.chinese_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        note = (
            "Tips: If YouTube desktop audio is needed, choose a loopback source named like "
            "'Speakers (...) [Loopback]'."
        )
        ttk.Label(self.root, text=note, padding=(12, 0, 12, 8)).pack(anchor=tk.W)

        top.columnconfigure(1, weight=1)

    def _refresh_sources(self) -> None:
        try:
            self.loopback_mics = sc.all_microphones(include_loopback=True)
        except Exception as exc:
            messagebox.showerror("Audio Error", f"Failed to enumerate audio devices: {exc}")
            return

        if not self.loopback_mics:
            self.source_combo["values"] = ["No devices found"]
            self.selected_mic_index.set("No devices found")
            self.status_text.set("No audio sources available")
            return

        labels: list[str] = []
        default_idx = 0
        for idx, mic in enumerate(self.loopback_mics):
            label = f"{idx}: {mic.name}"
            labels.append(label)
            name_lower = mic.name.lower()
            if "loopback" in name_lower or "stereo mix" in name_lower:
                default_idx = idx

        self.source_combo["values"] = labels
        self.selected_mic_index.set(labels[default_idx])
        self.status_text.set(f"Loaded {len(labels)} sources")

    def _ensure_model(self) -> None:
        if self.model is None:
            self.status_text.set("Loading Whisper model...")
            self.root.update_idletasks()
            self.model = WhisperModel(self.model_size.get(), device="cpu", compute_type="int8")
            self.status_text.set("Model loaded")

    def _parse_selected_index(self) -> int:
        text = self.selected_mic_index.get().strip()
        if not text or ":" not in text:
            raise ValueError("Please choose a valid audio source")
        return int(text.split(":", 1)[0])

    def start(self) -> None:
        if self.running:
            return

        try:
            mic_idx = self._parse_selected_index()
        except Exception as exc:
            messagebox.showwarning("Source", str(exc))
            return

        if mic_idx < 0 or mic_idx >= len(self.loopback_mics):
            messagebox.showwarning("Source", "Selected source index is out of range")
            return

        try:
            self._ensure_model()
        except Exception as exc:
            messagebox.showerror("Model", f"Failed to load Whisper model: {exc}")
            return

        self.stop_event.clear()
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_text.set("Running...")

        mic = self.loopback_mics[mic_idx]
        self.worker_thread = threading.Thread(target=self._worker, args=(mic,), daemon=True)
        self.worker_thread.start()

    def stop(self) -> None:
        if not self.running:
            return

        self.stop_event.set()
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_text.set("Stopping...")

    def clear_text(self) -> None:
        self.english_box.delete("1.0", tk.END)
        self.chinese_box.delete("1.0", tk.END)

    def _worker(self, mic: sc.Microphone) -> None:
        sample_rate = 16000
        chunk = max(1.5, float(self.chunk_seconds.get()))
        frames = int(sample_rate * chunk)

        try:
            with mic.recorder(samplerate=sample_rate, channels=1, blocksize=frames) as recorder:
                while not self.stop_event.is_set():
                    audio = recorder.record(numframes=frames)
                    if audio is None or len(audio) == 0:
                        continue

                    # Skip very quiet chunks to reduce useless inference calls.
                    energy = float(np.abs(audio).mean())
                    if energy < 0.003:
                        continue

                    audio_flat = np.asarray(audio, dtype=np.float32).flatten()
                    segments, _ = self.model.transcribe(
                        audio_flat,
                        language="en",
                        vad_filter=True,
                        beam_size=1,
                        condition_on_previous_text=False,
                    )

                    text_parts = [seg.text.strip() for seg in segments if seg.text.strip()]
                    en_text = " ".join(text_parts).strip()
                    if not en_text:
                        continue

                    self.ui_queue.put(("en", en_text))

                    try:
                        zh_text = self.translator.translate(en_text)
                    except Exception as exc:
                        zh_text = f"[Translation error] {exc}"

                    self.ui_queue.put(("zh", zh_text))
        except Exception as exc:
            self.ui_queue.put(("status", f"Audio worker stopped: {exc}"))
        finally:
            self.ui_queue.put(("stopped", "Stopped"))

    def _schedule_ui_updates(self) -> None:
        self._drain_ui_queue()
        self.root.after(200, self._schedule_ui_updates)

    def _drain_ui_queue(self) -> None:
        while True:
            try:
                kind, payload = self.ui_queue.get_nowait()
            except queue.Empty:
                break

            if kind == "en":
                self.english_box.insert(tk.END, payload + "\n")
                self.english_box.see(tk.END)
            elif kind == "zh":
                self.chinese_box.insert(tk.END, payload + "\n")
                self.chinese_box.see(tk.END)
            elif kind == "status":
                self.status_text.set(payload)
            elif kind == "stopped":
                self.running = False
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.status_text.set("Stopped")


def main() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")

    app = RealtimeTranslatorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
