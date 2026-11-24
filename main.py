import os
import threading
from tkinter import filedialog
import numpy as np
import pydicom
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from skimage.transform import radon, iradon, resize

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TRANSLATIONS = {
    "TR": {
        "title": "CT Digital Twin - BT Simülasyon Sistemi",
        "load_btn": "1. Veri Setini Yükle",
        "browse_btn": "Farklı Klasör Seç",
        "sim_btn": "2. Simülasyon Başlat",
        "history_default": "Simülasyon Geçmişi",
        "case_prefix": "Vaka",
        "prev_btn": "< Önceki",
        "next_btn": "Sonraki >",
        "status_ready": "Hazır. Lütfen veri setini yükleyin.",
        "status_loading": "DICOM dosyaları taranıyor...",
        "status_loaded": "{count} geçerli DICOM dosyası yüklendi.",
        "status_empty": "Klasörde geçerli .dcm dosyası bulunamadı!",
        "status_not_found": "HATA: Klasör yolu bulunamadı!",
        "status_simulating": "Radon simülasyonu hesaplanıyor...",
        "status_sim_done": "{case} tamamlandı.",
        "status_load_first": "Önce geçerli bir veri seti yükleyin!",
        "plot_orig": "Orijinal BT Kesiti",
        "plot_sino": "Sinogram (Radon)",
        "plot_recon": "Rekonstrüksiyon (iRadon)",
        "dialog_title": "DICOM Klasörü Seçin",
    },
    "EN": {
        "title": "CT Digital Twin - CT Simulation System",
        "load_btn": "1. Load Dataset",
        "browse_btn": "Browse Folder",
        "sim_btn": "2. Run Simulation",
        "history_default": "Simulation History",
        "case_prefix": "Case",
        "prev_btn": "< Prev",
        "next_btn": "Next >",
        "status_ready": "Ready. Please load the dataset.",
        "status_loading": "Scanning DICOM files...",
        "status_loaded": "{count} valid DICOM files loaded.",
        "status_empty": "No valid .dcm files found in folder!",
        "status_not_found": "ERROR: Folder path not found!",
        "status_simulating": "Computing Radon simulation...",
        "status_sim_done": "{case} completed.",
        "status_load_first": "Please load a valid dataset first!",
        "plot_orig": "Original CT Slice",
        "plot_sino": "Sinogram (Radon)",
        "plot_recon": "Reconstruction (iRadon)",
        "dialog_title": "Select DICOM Folder",
    },
}


class CTDigitalTwinSystem:
    def __init__(self):
        self.history = {}
        self.case_counter = 0
        self.dicom_files = []

    def load_and_clean_data(self, folder_path):
        files_found = []

        if not os.path.exists(folder_path):
            return "not_found", 0

        for root, _, files in os.walk(folder_path):
            for f in files:
                if f.lower().endswith(".dcm"):
                    path = os.path.join(root, f)
                    try:
                        ds = pydicom.dcmread(path, stop_before_pixels=True)
                        if hasattr(ds, "Rows") and hasattr(ds, "Columns"):
                            files_found.append(path)
                    except Exception:
                        continue

        self.dicom_files = files_found
        if not self.dicom_files:
            return "empty", 0
        return "loaded", len(self.dicom_files)

    def run_simulation(self, target_size=256):
        if not self.dicom_files:
            return None

        idx = np.random.randint(0, len(self.dicom_files))
        ds = pydicom.dcmread(self.dicom_files[idx])
        image = ds.pixel_array.astype(np.float32)

        if image.ndim == 3:
            image = image[image.shape[0] // 2]

        if image.shape[0] != target_size or image.shape[1] != target_size:
            image = resize(
                image,
                (target_size, target_size),
                anti_aliasing=True,
                preserve_range=True,
            ).astype(np.float32)

        min_val, max_val = np.min(image), np.max(image)
        if max_val - min_val != 0:
            image = (image - min_val) / (max_val - min_val)

        theta = np.linspace(0.0, 180.0, 180, endpoint=False)
        sinogram = radon(image, theta=theta, circle=True).astype(np.float32)
        reconstruction = iradon(sinogram, theta=theta, filter_name="ramp", circle=True).astype(np.float32)

        self.case_counter += 1
        case_num = self.case_counter

        self.history[case_num] = {
            "original": image,
            "sinogram": sinogram,
            "recon": reconstruction,
        }
        return case_num


class App(ctk.CTk):
    def __init__(self, system):
        super().__init__()
        self.system = system
        self.lang = "TR"
        self.current_case = None
        self.status_state = ("status_ready", {})

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.default_data_dir = os.path.join(base_dir, "data", "dicom")
        os.makedirs(self.default_data_dir, exist_ok=True)

        self.title(self.t("title"))
        self.geometry("1160x620")
        self.minsize(960, 520)

        self.grid_columnconfigure(0, weight=0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_propagate(False)
        self.sidebar.pack_propagate(False)

        self.lang_switch = ctk.CTkSegmentedButton(
            self.sidebar,
            values=["TR", "EN"],
            command=self.change_language,
        )
        self.lang_switch.set("TR")
        self.lang_switch.pack(pady=(15, 20), padx=15, fill="x")

        self.btn_load = ctk.CTkButton(
            self.sidebar,
            text=self.t("load_btn"),
            command=lambda: self.load_data(self.default_data_dir),
        )
        self.btn_load.pack(pady=6, padx=15, fill="x")

        self.btn_browse = ctk.CTkButton(
            self.sidebar,
            text=self.t("browse_btn"),
            fg_color="transparent",
            border_width=1,
            command=self.browse_folder,
        )
        self.btn_browse.pack(pady=6, padx=15, fill="x")

        self.status = ctk.CTkLabel(
            self.sidebar,
            text=self.t("status_ready"),
            wraplength=215,
            height=48,
            justify="center",
        )
        self.status.pack(pady=10, padx=15, fill="x")

        self.btn_sim = ctk.CTkButton(
            self.sidebar,
            text=self.t("sim_btn"),
            command=self.start_sim,
        )
        self.btn_sim.pack(pady=10, padx=15, fill="x")

        self.menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=[self.t("history_default")],
            command=self.on_select_case,
        )
        self.menu.pack(pady=(12, 6), padx=15, fill="x")

        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.pack(pady=4, padx=15, fill="x")
        self.nav_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_prev = ctk.CTkButton(
            self.nav_frame,
            text=self.t("prev_btn"),
            height=28,
            fg_color="transparent",
            border_width=1,
            command=self.prev_case,
        )
        self.btn_prev.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_next = ctk.CTkButton(
            self.nav_frame,
            text=self.t("next_btn"),
            height=28,
            fg_color="transparent",
            border_width=1,
            command=self.next_case,
        )
        self.btn_next.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        self.fig, self.axs = plt.subplots(1, 3, figsize=(10, 4.5), dpi=100)
        self.fig.patch.set_facecolor("#2b2b2b")
        self.fig.subplots_adjust(left=0.03, right=0.97, top=0.88, bottom=0.05, wspace=0.10)
        for ax in self.axs:
            ax.set_facecolor("#1e1e1e")
            ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

    def t(self, key, **kwargs):
        text = TRANSLATIONS[self.lang][key]
        return text.format(**kwargs) if kwargs else text

    def set_status(self, key, **kwargs):
        self.status_state = (key, kwargs)
        self.status.configure(text=self.t(key, **kwargs))

    def set_controls_state(self, state):
        self.btn_load.configure(state=state)
        self.btn_browse.configure(state=state)
        self.btn_sim.configure(state=state)
        self.btn_prev.configure(state=state)
        self.btn_next.configure(state=state)

    def change_language(self, new_lang):
        self.lang = new_lang
        self.title(self.t("title"))
        self.btn_load.configure(text=self.t("load_btn"))
        self.btn_browse.configure(text=self.t("browse_btn"))
        self.btn_sim.configure(text=self.t("sim_btn"))
        self.btn_prev.configure(text=self.t("prev_btn"))
        self.btn_next.configure(text=self.t("next_btn"))

        key, kwargs = self.status_state
        display_kwargs = kwargs.copy()
        if "case" in display_kwargs and self.current_case is not None:
            display_kwargs["case"] = f"{self.t('case_prefix')} #{self.current_case}"
        self.status.configure(text=self.t(key, **display_kwargs))

        self.refresh_history_menu()
        if self.current_case is not None:
            self.display(self.current_case)

    def refresh_history_menu(self):
        if not self.system.history:
            self.menu.configure(values=[self.t("history_default")])
            self.menu.set(self.t("history_default"))
        else:
            prefix = self.t("case_prefix")
            labels = [f"{prefix} #{num}" for num in self.system.history.keys()]
            self.menu.configure(values=labels)
            if self.current_case in self.system.history:
                self.menu.set(f"{prefix} #{self.current_case}")

    def browse_folder(self):
        folder = filedialog.askdirectory(title=self.t("dialog_title"))
        if folder:
            self.load_data(folder)

    def load_data(self, folder_path):
        self.set_controls_state("disabled")
        self.set_status("status_loading")
        threading.Thread(target=self._load_worker, args=(folder_path,), daemon=True).start()

    def _load_worker(self, folder_path):
        status_code, count = self.system.load_and_clean_data(folder_path)
        self.after(0, self._on_load_complete, status_code, count)

    def _on_load_complete(self, status_code, count):
        self.set_controls_state("normal")
        if status_code == "loaded":
            self.set_status("status_loaded", count=count)
        elif status_code == "empty":
            self.set_status("status_empty")
        else:
            self.set_status("status_not_found")

    def start_sim(self):
        if not self.system.dicom_files:
            self.set_status("status_load_first")
            return

        self.set_controls_state("disabled")
        self.set_status("status_simulating")
        threading.Thread(target=self._sim_worker, daemon=True).start()

    def _sim_worker(self):
        case_num = self.system.run_simulation()
        self.after(0, self._on_sim_complete, case_num)

    def _on_sim_complete(self, case_num):
        self.set_controls_state("normal")
        if case_num is not None:
            self.current_case = case_num
            self.refresh_history_menu()
            case_label = f"{self.t('case_prefix')} #{case_num}"
            self.set_status("status_sim_done", case=case_label)
            self.display(case_num)

    def on_select_case(self, selection):
        if "#" in selection:
            case_num = int(selection.split("#")[1])
            self.current_case = case_num
            self.display(case_num)

    def prev_case(self):
        keys = list(self.system.history.keys())
        if not keys or self.current_case not in keys:
            return
        idx = keys.index(self.current_case)
        if idx > 0:
            self.current_case = keys[idx - 1]
            self.refresh_history_menu()
            self.display(self.current_case)

    def next_case(self):
        keys = list(self.system.history.keys())
        if not keys or self.current_case not in keys:
            return
        idx = keys.index(self.current_case)
        if idx < len(keys) - 1:
            self.current_case = keys[idx + 1]
            self.refresh_history_menu()
            self.display(self.current_case)

    def display(self, case_num):
        data = self.system.history[case_num]
        titles = [self.t("plot_orig"), self.t("plot_sino"), self.t("plot_recon")]
        images = [data["original"], data["sinogram"], data["recon"]]
        aspects = ["equal", "auto", "equal"]

        for ax, img, title, aspect in zip(self.axs, images, titles, aspects):
            ax.clear()
            ax.imshow(img, cmap="gray", aspect=aspect)
            ax.set_title(title, color="white", fontsize=11, pad=8)
            ax.axis("off")

        self.canvas.draw_idle()


if __name__ == "__main__":
    app = App(CTDigitalTwinSystem())
    app.mainloop()