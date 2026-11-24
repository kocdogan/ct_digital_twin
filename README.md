# CT Digital Twin

[Türkçe](#türkçe-tr) | [English](#english-en)

---

## Türkçe (TR)

Tıbbi **DICOM (`.dcm`)** formatındaki Bilgisayarlı Tomografi (BT) kesitleri üzerinde **Radon Dönüşümü (Sinogram üretimi)** ve **Ters Radon Dönüşümü (Filtered Back Projection - iRadon rekonstrüksiyonu)** süreçlerini görselleştiren masaüstü simülasyon aracıdır.

### Özellikler
* **Çift Dil Desteği (TR / EN):** Arayüz üzerinden yeniden başlatmaya gerek kalmadan anlık Türkçe ve İngilizce dil geçişi.
* **Asenkron ve Hızlı İşleme:** Çoklu iş parçacığı (`threading`) ve başlık tabanlı hızlı tarama (`stop_before_pixels`) sayesinde arayüz donmadan kesintisiz simülasyon.
* **Vaka Geçmişi Gezgini:** Çalıştırılan tüm simülasyonları bellekte tutar; açılır menü veya `< Önceki` / `Sonraki >` butonları ile geçmiş vakalar arasında geçiş imkânı sunar.

### Kurulum

1. Depoyu bilgisayarınıza indirin:
   ```bash
   git clone https://github.com/kocdogan/ct_digital_twin.git
   cd ct_digital_twin
   ```

2. Gerekli Python kütüphanelerini yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

### `data` Klasörüne Ne Yüklenmeli?

Programın çalışabilmesi için gerçek veya anonimleştirilmiş **BT (CT) DICOM (`.dcm`)** dosyalarına ihtiyacı vardır.

1. Bilgisayarınızdaki **`.dcm`** uzantılı tomografi kesitlerini proje içindeki **`data/dicom/`** klasörüne kopyalayın (alt klasörler halinde atsanız da program otomatik tarar):
   ```text
   ct_digital_twin/
   ├── data/
   │   └── dicom/
   │       ├── slice_001.dcm
   │       ├── slice_002.dcm
   │       └── ...
   ├── main.py
   ├── requirements.txt
   └── README.md
   ```
2. Dosyaları bu klasöre taşımak istemezseniz, uygulama içindeki **"Farklı Klasör Seç"** butonunu kullanarak bilgisayarınızdaki herhangi bir DICOM dizinini seçebilirsiniz.

**Örnek DICOM Veri Seti Kaynakları:**
* **The Cancer Imaging Archive (TCIA):** Ücretsiz klinik BT veri setleri (*LIDC-IDRI*, *CT Colonography* vb.).
* **Kaggle:** `"CT Medical Images"` veya `"DICOM CT scans"` aramalarıyla erişilebilen açık veri paketleri.

> **Not:** Hasta gizliliği ve dosya boyutu sınırları nedeniyle bu depoda örnek hasta görüntüsü paylaşılmamıştır.

### Kullanım

```bash
python main.py
```

1. Sol üst panelden **TR** veya **EN** dilini seçin.
2. **"1. Veri Setini Yükle"** butonuna tıklayarak `data/dicom` klasöründeki geçerli `.dcm` dosyalarını taratın.
3. **"2. Simülasyon Başlat"** butonuna basarak rastgele seçilen bir BT kesitinin **Orijinal BT Kesiti**, **Sinogram (Radon)** ve **Rekonstrüksiyon (iRadon)** çıktılarını inceleyin.

---

## English (EN)

A desktop simulation tool that visualizes **Radon Transform (Sinogram generation)** and **Inverse Radon Transform (Filtered Back Projection - iRadon reconstruction)** workflows on medical **DICOM (`.dcm`)** Computed Tomography (CT) slices.

### Features
* **Bilingual Interface (TR / EN):** Instant switching between Turkish and English directly from the UI without restarting.
* **Asynchronous & Fast Processing:** Multi-threaded execution (`threading`) combined with header-only metadata scanning (`stop_before_pixels`) prevents UI freezing during folder scans and simulations.
* **Case History Navigator:** Retains all simulated cases in memory; browse previous results via the dropdown menu or `< Prev` / `Next >` navigation buttons.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kocdogan/ct_digital_twin.git
   cd ct_digital_twin
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Dataset Setup (What to Put in the `data` Folder)

The application requires real or anonymized **CT DICOM (`.dcm`)** slice files to run simulations.

1. Place your **`.dcm`** tomography files inside the **`data/dicom/`** directory (subfolders are scanned automatically):
   ```text
   ct_digital_twin/
   ├── data/
   │   └── dicom/
   │       ├── slice_001.dcm
   │       ├── slice_002.dcm
   │       └── ...
   ├── main.py
   ├── requirements.txt
   └── README.md
   ```
2. Alternatively, use the **"Browse Folder"** button inside the app to select any DICOM directory on your system without moving files.

**Public DICOM Dataset Sources:**
* **The Cancer Imaging Archive (TCIA):** Open-access clinical CT collections (e.g., *LIDC-IDRI*, *CT Colonography*).
* **Kaggle:** Public datasets available under `"CT Medical Images"` or `"DICOM CT scans"`.

> **Note:** Sample patient scans are excluded from this repository due to patient privacy regulations and file size limits.

### Usage

```bash
python main.py
```

1. Select **TR** or **EN** from the top-left language switch.
2. Click **"1. Load Dataset"** to scan valid `.dcm` files in `data/dicom`.
3. Click **"2. Run Simulation"** to inspect the **Original CT Slice**, **Sinogram (Radon)**, and **Reconstruction (iRadon)** outputs of a randomly selected slice.