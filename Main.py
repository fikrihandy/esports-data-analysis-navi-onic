import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
# Mengatur konfigurasi halaman sebagai perintah pertama
st.set_page_config(layout="wide", page_title="Analisis Jungler MLBB")


# --- PEMUATAN & PEMROSESAN DATA (DENGAN CACHING) ---
@st.cache_data
def load_data():
    """
    Memuat, memproses, dan menambahkan kolom metrik baru.
    Fungsi ini di-cache untuk meningkatkan performa aplikasi.
    """
    try:
        stats_df = pd.read_csv('data_jungler/statistics.csv')
        hero_pool_df = pd.read_csv('data_jungler/hero_pool.csv')
    except FileNotFoundError:
        st.error("Pastikan file 'statistics.csv' dan 'hero_pool.csv' ada.")
        return None, None

    # Filter data yang valid
    stats_df = stats_df[stats_df['Games Played'] > 0].reset_index(drop=True)

    # --- Feature Engineering ---
    stats_df['Turtles per Game'] = stats_df['Cryoturtle Secured'] / stats_df['Games Played']
    stats_df['Lords per Game'] = stats_df['Lord Secured'] / stats_df['Games Played']
    stats_df['Towers per Game'] = stats_df['Towers Secured'] / stats_df['Games Played']
    stats_df['First Blood Rate'] = stats_df['First Blood'] / stats_df['Games Played']
    stats_df.replace([np.inf, -np.inf], 0, inplace=True)

    return stats_df, hero_pool_df


# --- FUNGSI UNTUK KONVERSI KE CSV ---
@st.cache_data
def convert_df_to_csv(df):
    # Penting: Gunakan to_csv untuk mengonversi DataFrame ke CSV string
    return df.to_csv(index=False).encode('utf-8')


# --- HALAMAN 1: ANALISIS DETAIL PEMAIN ---
def page_player_analysis(stats_df, hero_pool_df):
    st.title("📊 Stats Jungler MLBB")

    # Pemilihan Pemain
    player_list = sorted(stats_df['Player'].unique())
    selected_player = st.selectbox("Pilih Jungler:", player_list)

    # Filter data untuk pemain terpilih
    player_stats = stats_df[stats_df['Player'] == selected_player].iloc[0]
    player_hero_pool = hero_pool_df[hero_pool_df['Player ID'] == player_stats['ID']]
    league_avg = stats_df.mean(numeric_only=True)

    st.header(f"Stats: {selected_player}")

    # Tampilan Metrik Detail
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Matches Played", value=int(player_stats['Matches Played']))
    with col2:
        st.metric(label="Games Played", value=int(player_stats['Games Played']))
    with col3:
        st.metric(label="Games Win Ratio", value=f"{player_stats['Games Win Ratio%']:.2f}%")
    with col4:
        st.metric(label="KDA Ratio", value=f"{player_stats['KDA Ratio']:.2f}",
                  delta=f"{(player_stats['KDA Ratio'] - league_avg['KDA Ratio']):.2f} vs Avg")
    st.markdown("---")
    cat1, cat2 = st.columns(2)
    with cat1:
        st.subheader("1. Objektif (per Game)")
        obj_col1, obj_col2, obj_col3 = st.columns(3)
        obj_col1.metric("Turtles per Game", f"{player_stats['Turtles per Game']:.2f}",
                        f"{(player_stats['Turtles per Game'] - league_avg['Turtles per Game']):.2f}")
        obj_col2.metric("Lords per Game", f"{player_stats['Lords per Game']:.2f}",
                        f"{(player_stats['Lords per Game'] - league_avg['Lords per Game']):.2f}")
        obj_col3.metric("Towers per Game", f"{player_stats['Towers per Game']:.2f}",
                        f"{(player_stats['Towers per Game'] - league_avg['Towers per Game']):.2f}")
    with cat2:
        st.subheader("2. Farming & Leveling")
        farm_col1, farm_col2, farm_col3 = st.columns(3)
        farm_col1.metric("Gold Per Minute (GPM)", f"{player_stats['Gold Per Minute']:.2f}",
                         f"{(player_stats['Gold Per Minute'] - league_avg['Gold Per Minute']):.2f}")
        farm_col2.metric("EXP Per Minute (XPM)", f"{player_stats['Exp Per Minute']:.2f}",
                         f"{(player_stats['Exp Per Minute'] - league_avg['Exp Per Minute']):.2f}")
        farm_col3.metric("Gold Share %", f"{player_stats['Gold Share%']:.2f}%",
                         f"{(player_stats['Gold Share%'] - league_avg['Gold Share%']):.2f}%")
    st.markdown("---")
    cat3, cat4 = st.columns(2)
    with cat3:
        st.subheader("3. Teamfight")
        kda_col1, kda_col2, kda_col3 = st.columns(3)
        kda_col1.metric("Avg Kills", f"{player_stats['Average Kills per game']:.2f}")
        kda_col2.metric("Avg Deaths", f"{player_stats['Average Deaths']:.2f}", delta_color="inverse")
        kda_col3.metric("Avg Assists", f"{player_stats['Average Assists']:.2f}")
        st.metric("Kill Participation %", f"{player_stats['Kill Participation%']:.2f}%",
                  f"{(player_stats['Kill Participation%'] - league_avg['Kill Participation%']):.2f}%")
    with cat4:
        st.subheader("4. Output & Efisiensi Damage")
        dmg_col1, dmg_col2, dmg_col3 = st.columns(3)
        dmg_col1.metric("Damage Per Minute", f"{player_stats['Damage Per Minute']:.2f}",
                        f"{(player_stats['Damage Per Minute'] - league_avg['Damage Per Minute']):.2f}")
        dmg_col2.metric("Damage Share %", f"{player_stats['Damage Share%']:.2f}%",
                        f"{(player_stats['Damage Share%'] - league_avg['Damage Share%']):.2f}%")
        dmg_col3.metric("Damage/Gold %", f"{player_stats['Damage/Gold%']:.2f}%",
                        f"{(player_stats['Damage/Gold%'] - league_avg['Damage/Gold%']):.2f}%")
    st.markdown("---")

    # Analisis Hero Pool
    st.header("Hero Pool")
    if not player_hero_pool.empty:
        hero_pool_display = player_hero_pool[['Hero', 'Game Count', 'Game Win Rate%', 'KDA']].sort_values(
            by="Game Count", ascending=False).reset_index(drop=True)
        st.dataframe(hero_pool_display, use_container_width=True)
    else:
        st.write("Data hero pool tidak ditemukan untuk pemain ini.")


# --- FUNGSI HALAMAN 2: TABEL STATISTIK KESELURUHAN ---
def page_summary_table(stats_df):
    st.title("📋 All Stats + Conclusion")

    # Pilih dan ganti nama kolom
    summary_cols = {
        'Player': 'Player',
        'Games Played': 'Total Game (Experience)',
        'Games Win Ratio%': 'Win Rate %',
        'KDA Ratio': 'KDA',
        'Average Kills per game': 'Avg Kills',
        'Average Deaths': 'Avg Deaths',
        'Average Assists': 'Avg Assists',
        'Gold Per Minute': 'GPM',
        'Damage Per Minute': 'DPM',
        'Kill Participation%': 'KP %',
        'Turtles per Game': 'Turtle/Game',
        'Lords per Game': 'Lord/Game'
    }

    # Buat dua salinan: satu untuk tampilan (string) dan satu untuk visualisasi (numeric)
    summary_display_df = stats_df[list(summary_cols.keys())].copy()
    summary_display_df.rename(columns=summary_cols, inplace=True)

    summary_viz_df = summary_display_df.copy()  # Salinan ini tetap numeric

    # Format angka untuk tampilan tabel
    for col in summary_display_df.columns:
        if pd.api.types.is_numeric_dtype(summary_display_df[col]) and col != 'Total Game':
            summary_display_df[col] = summary_display_df[col].apply(lambda x: f'{x:.2f}')

    # Download CSV
    csv_data = convert_df_to_csv(summary_display_df)  # Gunakan df yang sudah diformat
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name='summary_stats_jungler.csv',
        mime='text/csv',
    )

    # Tampilkan DataFrame
    st.dataframe(summary_display_df, use_container_width=True)

    st.markdown("---")

    # ====================================================================
    # --- BAGIAN VISUALISASI PERBANDINGAN PEMAIN ---
    # ====================================================================

    st.subheader("Heatmap")
    st.write(
        "Warna hijau menandakan rank atas, dan warna merah menandakan rank bawah."
    )

    # 1. Siapkan DataFrame asli untuk TEKS yang akan ditampilkan
    heatmap_text_df = summary_viz_df.set_index('Player')

    # 2. Buat salinan terpisah yang nilainya akan diubah untuk PEWARNAAN
    heatmap_color_df = heatmap_text_df.copy()

    # 3. Balik logika 'Avg Deaths' HANYA untuk DataFrame pewarnaan
    if 'Avg Deaths' in heatmap_color_df.columns:
        max_deaths = heatmap_color_df['Avg Deaths'].max()
        heatmap_color_df['Avg Deaths'] = max_deaths - heatmap_color_df['Avg Deaths']

    # 4. Normalisasi DataFrame pewarnaan agar skala warna benar
    normalized_color_df = heatmap_color_df.apply(lambda x: (x - x.min()) / (x.max() - x.min()))

    # 5. Buat heatmap menggunakan data normalisasi untuk WARNA
    fig = px.imshow(
        normalized_color_df,
        text_auto=False,
        aspect="auto",
        color_continuous_scale='RdYlGn',
        labels=dict(color="Relative Ranking"),
        x=heatmap_text_df.columns,
        y=heatmap_text_df.index
    )

    fig.update_traces(
        text=heatmap_text_df,  # Gunakan DataFrame asli untuk teks
        texttemplate="%{text:.2f}"  # Format teks dengan 2 angka desimal
    )

    fig.update_layout(
        title_text='Perbandingan Statistik Antar Pemain',
        title_x=0.5,
        xaxis_title="Stats",
        yaxis_title="Jungler"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ====================================================================
    # --- BAGIAN KESIMPULAN DAN REKOMENDASI ---
    # ====================================================================

    st.markdown("""
    ## 🏆 **Kesimpulan & Rekomendasi Jungler**

    ### ✅ **1. Gugunnn**
    - Performa individu tinggi di KDA, Assist, DPM, dan objektif (Lord/Game).
    - Pengalaman di MPL-ID Season 13-14 bersama AURA/TLID. 46 game dimainkan dengan WR 45.65%.
    - Cocok untuk tim yang mencari jungler dengan gaya main agresif dan kontribusi tinggi.

    ---

    ### ✅ **2. Nnael**
    - Jam terbang tinggi, konsisten dan stabil, stats berada di level rata-rata.
    - Bermain 104 game (WR 49.04%) di MPL-ID S12 (GEEK FAM) dan S14 (ALTER EGO)

    ---

    ### ✅ **3. Andoryuuu**
    - Bermain di MPL PH (liga kompetitif).
    - Stats baik, terutama **DPM** dan **KP%**.
    - Ideal untuk mencari pengalaman lintas regional dan perspektif gameplay PH.

    ---

    ### ✅ **4. Anavel**
    - Pengalaman di MPL ID (S13–S15), statistik cukup stabil.
    - Berpengalaman dan konsisten

    ---

    ### ⚠️ **5. Bouy**
    - Statistik baik, namun belum punya pengalaman di MPL.
    - **Hanya bermain di tier B/C**, jumlah game sedikit (22).
    - Direkomendasikan untuk proyek jangka panjang, perlu membuktikan kemampuannya di level MPL.

    ---

    ### ⚠️ **6. Woshipaul**
    - WR sangat rendah (9.52%) di MPL-ID S15, kontribusi objektif dan statistik individu rendah.
    - Perlu pengembangan lebih lanjut.

    ---
    """)

# --- MAIN APP LOGIC ---
def main():
    stats_df, hero_pool_df = load_data()

    if stats_df is not None and hero_pool_df is not None:
        # Navigasi Sidebar
        st.sidebar.title("Navigasi")
        page_options = {
            "All Stats + Conclusion": (page_summary_table, (stats_df,)),
            "Detail Stats + Hero Pool": (page_player_analysis, (stats_df, hero_pool_df))
        }
        selected_page = st.sidebar.radio("Pilih Halaman:", list(page_options.keys()))

        # Panggil fungsi halaman yang dipilih
        page_function, args = page_options[selected_page]
        page_function(*args)


if __name__ == "__main__":
    main()