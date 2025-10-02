"""GUI Aplikasi Pemantauan Gas Rumah Kaca Jakarta (CO₂ & CH₄) berbasis Open-Meteo API."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta

import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from tkcalendar import DateEntry

plt.style.use('ggplot')

# =============================
# Koordinat Wilayah Jakarta
# =============================
wilayah_coords = {
    "Jakarta Pusat": (-6.1862, 106.8347),
    "Jakarta Barat": (-6.1683, 106.7589),
    "Jakarta Timur": (-6.2250, 106.9000),
    "Jakarta Selatan": (-6.2667, 106.8000),
    "Jakarta Utara": (-6.1189, 106.9156),
    "Pulau Seribu": (-5.7980, 106.5070)
}

# =============================
# Fungsi ambil data Open-Meteo
# =============================
def get_air_quality_data(lat, lon):
    """Mengambil data kualitas udara (CO₂ & CH₄) dari API Open-Meteo.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.

    Returns:
        pd.DataFrame: Data waktu, CO₂ (ppm), CH₄ (ppb).
    """
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "carbon_dioxide,methane",
        "past_days": 7,
        "forecast_days": 2
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if "hourly" not in data:
            return pd.DataFrame({"Waktu": [], "CO2_ppm": [], "CH4_ppb": []})
        times = pd.to_datetime(data["hourly"]["time"])
        co2 = data["hourly"]["carbon_dioxide"]
        ch4 = data["hourly"]["methane"]
        return pd.DataFrame({"Waktu": times, "CO2_ppm": co2, "CH4_ppb": ch4})
    except Exception:
        return pd.DataFrame({"Waktu": [], "CO2_ppm": [], "CH4_ppb": []})


# =============================
# GUI Utama
# =============================
root = tk.Tk()
root.title("Aplikasi Pemantauan Gas Rumah Kaca Jakarta")
root.geometry("1200x850")
root.configure(bg="#ECEFF1")

header = tk.Label(
    root,
    text="Aplikasi Pemantauan Gas Rumah Kaca Jakarta: CO₂ & CH₄ Berbasis Open Data",
    font=("Segoe UI", 16, "bold"),
    bg="#0D47A1",
    fg="white",
    pady=12
)
header.pack(fill="x")

main_frame = tk.Frame(root, bg="#ECEFF1")
main_frame.pack(fill="both", expand=True)

sidebar = tk.Frame(main_frame, width=230, bg="#263238")
sidebar.pack(side="left", fill="y")

content_frame = tk.Frame(main_frame, bg="#ECEFF1")
content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)


# =============================
# Handler tombol X
# =============================
def on_close():
    """Handler untuk menutup aplikasi."""
    if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin menutup aplikasi?"):
        root.destroy()
root.protocol("WM_DELETE_WINDOW", on_close)


# =============================
# Bersihkan konten
# =============================
def clear_content():
    """Menghapus semua widget dari content_frame."""
    for widget in content_frame.winfo_children():
        widget.destroy()


# =============================
# Fungsi Plot Grafik
# =============================
def plot_graph(df, graph_frame, title="CO₂ & CH₄"):
    """Menampilkan grafik CO₂ & CH₄ pada frame Tkinter.

    Args:
        df (pd.DataFrame): Data kualitas udara.
        graph_frame (tk.Frame): Frame target untuk grafik.
        title (str): Judul grafik.
    """
    for widget in graph_frame.winfo_children():
        widget.destroy()
    if df.empty:
        tk.Label(graph_frame, text="Tidak ada data tersedia.",
                 font=("Segoe UI", 12), bg="#ECEFF1").pack()
        return

    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df["Waktu"], df["CO2_ppm"],
             color="#1E88E5", marker="o", label="CO₂ (ppm)")
    ax1.set_xlabel("Waktu")
    ax1.set_ylabel("CO₂ (ppm)", color="#1E88E5")

    ax2 = ax1.twinx()
    ax2.plot(df["Waktu"], df["CH4_ppb"],
             color="#FB8C00", marker="s", label="CH₄ (ppb)")
    ax2.set_ylabel("CH₄ (ppb)", color="#FB8C00")

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax1.tick_params(axis="x", rotation=45, labelsize=8)
    ax1.tick_params(axis="y", labelsize=10)
    ax2.tick_params(axis="y", labelsize=10)
    ax1.set_title(title)

    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# =============================
# Fungsi KPI
# =============================
def show_kpi(df, kpi_frame):
    """Menampilkan indikator KPI berdasarkan rata-rata CO₂ & CH₄."""
    for widget in kpi_frame.winfo_children():
        widget.destroy()
    if df.empty:
        tk.Label(kpi_frame, text="Tidak ada data KPI.",
                 font=("Segoe UI", 12), bg="#ECEFF1").pack()
        return

    co2_avg = df["CO2_ppm"].mean()
    ch4_avg = df["CH4_ppb"].mean()

    # Status CO2
    if co2_avg < 450:
        status_co2 = "Normal"
    elif 450 <= co2_avg <= 500:
        status_co2 = "Waspada"
    else:
        status_co2 = "Tinggi"

    # Status CH4
    if ch4_avg < 1950:
        status_ch4 = "Normal"
    elif 1950 <= ch4_avg <= 2000:
        status_ch4 = "Waspada"
    else:
        status_ch4 = "Tinggi"

    status_levels = {"Normal": 1, "Waspada": 2, "Tinggi": 3}
    overall_status = max([status_co2, status_ch4],
                         key=lambda x: status_levels[x])
    status_colors = {"Normal": "#43A047",
                     "Waspada": "#FFA726",
                     "Tinggi": "#E53935"}
    status_color = status_colors[overall_status]

    tk.Label(
        kpi_frame,
        text=f"CO₂ Avg: {co2_avg:.1f} ppm | CH₄ Avg: {ch4_avg:.1f} ppb | "
             f"Status: {overall_status}",
        font=("Segoe UI", 12, "bold"),
        bg="#ECEFF1",
        fg=status_color
    ).pack()


# =============================
# Fungsi Tombol Simpan CSV
# =============================
def add_save_button(parent_frame, df, label="Simpan CSV"):
    """Menambahkan tombol untuk menyimpan DataFrame ke CSV."""
    for widget in parent_frame.pack_slaves():
        if getattr(widget, "is_save_button", False):
            widget.destroy()

    def save_csv():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title=label
        )
        if file_path:
            df.to_csv(file_path, index=False)

    btn = tk.Button(
        parent_frame,
        text=label,
        bg="#1E88E5",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        command=save_csv
    )
    btn.is_save_button = True
    btn.pack(pady=10)


# =============================
# Dashboard Realtime
# =============================
def show_realtime():
    """Menampilkan dashboard realtime (data hari ini)."""
    clear_content()
    tk.Label(content_frame, text="Dashboard Realtime (Hari ini)",
             font=("Segoe UI", 14, "bold"), bg="#ECEFF1").pack(pady=10)

    wilayah_var = tk.StringVar()
    wilayah_var.set(list(wilayah_coords.keys())[0])

    tk.Label(content_frame, text="Pilih Wilayah:",
             font=("Segoe UI", 12), bg="#ECEFF1").pack(pady=5)
    combobox = ttk.Combobox(
        content_frame,
        textvariable=wilayah_var,
        values=list(wilayah_coords.keys()),
        state="readonly"
    )
    combobox.pack(pady=5)

    graph_frame = tk.Frame(content_frame, bg="#ECEFF1")
    graph_frame.pack(pady=10, fill="both", expand=True)

    kpi_frame = tk.Frame(content_frame, bg="#ECEFF1")
    kpi_frame.pack(pady=10, fill="x")

    refresh_interval = 600000

    def update_graph():
        """Mengupdate grafik realtime."""
        lat, lon = wilayah_coords[wilayah_var.get()]
        df = get_air_quality_data(lat, lon)
        today = datetime.now().date()
        df_today = df[df["Waktu"].dt.date == today]
        plot_graph(df_today, graph_frame, title="CO₂ & CH₄ Hari Ini")
        show_kpi(df_today, kpi_frame)
        add_save_button(content_frame, df_today, label="Simpan CSV Realtime")
        root.after(refresh_interval, update_graph)

    combobox.bind("<<ComboboxSelected>>", lambda e: update_graph())
    update_graph()
# =============================
# Proyeksi Beberapa Jam Kedepan
# =============================
def show_forecast():
    """Menampilkan proyeksi beberapa jam ke depan untuk CO₂ & CH₄."""
    clear_content()
    tk.Label(content_frame,
             text="Proyeksi Beberapa Jam Kedepan CO₂ & CH₄",
             font=("Segoe UI", 14, "bold"), bg="#ECEFF1").pack(pady=10)

    wilayah_var = tk.StringVar()
    wilayah_var.set(list(wilayah_coords.keys())[0])

    tk.Label(content_frame, text="Pilih Wilayah:",
             font=("Segoe UI", 12), bg="#ECEFF1").pack(pady=5)
    combobox = ttk.Combobox(
        content_frame,
        textvariable=wilayah_var,
        values=list(wilayah_coords.keys()),
        state="readonly"
    )
    combobox.pack(pady=5)

    graph_frame = tk.Frame(content_frame, bg="#ECEFF1")
    graph_frame.pack(pady=10, fill="both", expand=True)

    refresh_interval = 600000

    def update_forecast():
        """Mengupdate grafik proyeksi (forecast)."""
        lat, lon = wilayah_coords[wilayah_var.get()]
        df = get_air_quality_data(lat, lon)
        now = datetime.now()
        df_forecast = df[df["Waktu"] > now]
        plot_graph(df_forecast, graph_frame, title="Forecast CO₂ & CH₄")
        add_save_button(content_frame, df_forecast, label="Simpan CSV Forecast")
        root.after(refresh_interval, update_forecast)

    combobox.bind("<<ComboboxSelected>>", lambda e: update_forecast())
    update_forecast()


# =============================
# Data Periode
# =============================
def show_data_periode():
    """Menampilkan data berdasarkan periode tanggal yang dipilih pengguna."""
    clear_content()
    tk.Label(content_frame, text="Data Periode CO₂ & CH₄",
             font=("Segoe UI", 14, "bold"), bg="#ECEFF1").pack(pady=10)

    wilayah_var = tk.StringVar()
    wilayah_var.set(list(wilayah_coords.keys())[0])

    tk.Label(content_frame, text="Pilih Wilayah:",
             font=("Segoe UI", 12), bg="#ECEFF1").pack()
    combobox = ttk.Combobox(
        content_frame,
        textvariable=wilayah_var,
        values=list(wilayah_coords.keys()),
        state="readonly"
    )
    combobox.pack(pady=5)

    max_days = 7
    today = datetime.today().date()
    min_date = today - timedelta(days=max_days)

    tk.Label(content_frame, text="Tanggal Mulai:",
             font=("Segoe UI", 12), bg="#ECEFF1").pack()
    start_cal = DateEntry(
        content_frame,
        width=12,
        background='darkblue',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        mindate=min_date,
        maxdate=today
    )
    start_cal.pack(pady=5)

    tk.Label(content_frame, text="Tanggal Akhir:",
             font=("Segoe UI", 12), bg="#ECEFF1").pack()
    end_cal = DateEntry(
        content_frame,
        width=12,
        background='darkblue',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        mindate=min_date,
        maxdate=today
    )
    end_cal.pack(pady=5)

    tree_frame = tk.Frame(content_frame)
    tree_frame.pack(pady=10, fill="both", expand=True)

    tree = ttk.Treeview(
        tree_frame,
        columns=("Waktu", "CO2_ppm", "CH4_ppb"),
        show="headings",
        height=15
    )
    tree.heading("Waktu", text="Waktu")
    tree.heading("CO2_ppm", text="CO₂ (ppm)")
    tree.heading("CH4_ppb", text="CH₄ (ppb)")
    tree.pack(fill="both", expand=True)

    def ambil_data():
        """Mengambil data dari API dan menampilkan pada tabel berdasarkan periode."""
        lat, lon = wilayah_coords[wilayah_var.get()]
        start_date = start_cal.get_date()
        end_date = end_cal.get_date()
        df = get_air_quality_data(lat, lon)
        df_period = df[(df["Waktu"].dt.date >= start_date) &
                       (df["Waktu"].dt.date <= end_date)]
        for i in tree.get_children():
            tree.delete(i)
        for _, row in df_period.iterrows():
            waktu_str = row["Waktu"].strftime("%Y-%m-%d %H:%M")
            tree.insert("", "end",
                        values=(waktu_str, row["CO2_ppm"], row["CH4_ppb"]))
        add_save_button(content_frame, df_period, label="Simpan CSV Periode")

    tk.Button(content_frame,
              text="Ambil Data",
              bg="#43A047",
              fg="white",
              font=("Segoe UI", 12, "bold"),
              command=ambil_data).pack(pady=10)


# =============================
# About + Disclaimer Hukum
# =============================
def show_about():
    """Menampilkan informasi aplikasi dan disclaimer hukum singkat."""
    clear_content()
    text = (
        "Aplikasi Pemantauan Gas Rumah Kaca Jakarta\n"
        "CO₂ & CH₄ Berbasis Open Data (Realtime + Proyeksi Beberapa Jam Kedepan)\n\n"
        "Versi: 1.0\n\n"
        "Fitur Utama:\n"
        "1. Dashboard Realtime\n"
        "   - Data Hari ini \n"
        "   - KPI (key performance indicator) & status kualitas udara\n"
        "   - Update otomatis tiap 10 menit\n"
        "   - Download CSV\n"
        "2. Proyeksi Beberapa Jam Kedepan\n"
        "   - Forecast CO₂ & CH₄\n"
        "   - Garis berbeda dari data realtime\n"
        "   - Update otomatis tiap 10 menit\n"
        "   - Download CSV\n"
        "3. Data Periode\n"
        "   - Maksimal 7 hari terakhir\n"
        "   - Pilih tanggal via kalender\n"
        "   - Download CSV\n\n"
        "Keterangan Ambang Batas CO₂ & CH₄ (luar ruangan):\n"
        "- CO₂ Normal: < 1000 ppm, Waspada: 1000–1500 ppm, Tinggi: > 1500 ppm \n"
        "- CH₄ Normal: < 1950 ppb, Waspada: 1950–2000 ppb, Tinggi: > 2000 ppb \n"
        "Sumber data: Global Carbon Project, WMO\n\n"
        "Disclaimer:\n"
        "1. Aplikasi ini hanya berfungsi sebagai antarmuka untuk menampilkan data publik\n"
        "   yang disediakan oleh Open-Meteo.\n"
        "2. Semua data yang ditampilkan merupakan milik Open-Meteo.\n"
        "3. Penggunaan aplikasi ini hanya untuk tujuan pendidikan, penelitian, dan\n"
        "   pemantauan ilmiah.\n"
        "4. Pengembang tidak bertanggung jawab atas keakuratan data Open-Meteo.\n"
        "5. Hak cipta atas data dan API tetap dimiliki oleh Open-Meteo. \n"
        "   Pengguna harus mematuhi ketentuan penggunaan Open-Meteo. \n"
    )
    tk.Label(content_frame, text=text, justify="left",
             font=("Segoe UI", 10), wraplength=800, bg="#ECEFF1").pack(pady=40,
                                                                      padx=40)


# =============================
# Sidebar Buttons
# =============================
tk.Button(sidebar,
          text="Dashboard Realtime",
          font=("Segoe UI", 12),
          width=26,
          bg="#37474F",
          fg="white",
          command=show_realtime).pack(pady=10)

tk.Button(sidebar,
          text="Proyeksi Beberapa Jam Kedepan",
          font=("Segoe UI", 12),
          width=26,
          bg="#37474F",
          fg="white",
          command=show_forecast).pack(pady=10)

tk.Button(sidebar,
          text="Data Periode",
          font=("Segoe UI", 12),
          width=26,
          bg="#37474F",
          fg="white",
          command=show_data_periode).pack(pady=10)

tk.Button(sidebar,
          text="About",
          font=("Segoe UI", 12),
          width=26,
          bg="#37474F",
          fg="white",
          command=show_about).pack(pady=10)


# =============================
# Footer
# =============================
footer = tk.Label(
    root,
    text=f"Update terakhir: {datetime.now().strftime('%d %b %Y %H:%M')}",
    font=("Segoe UI", 10),
    bg="#ECEFF1",
    pady=5
)
footer.pack(fill="x", side="bottom")


# =============================
# Default view & mainloop
# =============================
show_realtime()
root.mainloop()
