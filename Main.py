import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Analisis Kompetitif: NAVI vs ONIC",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_data(file_path):
    return pd.read_csv('data/' + file_path, sep=';')


@st.cache_data
def load_data_history():
    return pd.read_csv('data/navi_match_history_s15.csv', sep=',')


# Load semua data
team_stats = load_data('team_statistics.csv')
navi_player_stats = load_data('player_navi_statistics.csv')
onic_player_stats = load_data('player_onic_statistics.csv')
navi_hero_stats = load_data('navi_hero.csv')
onic_hero_stats = load_data('onic_hero.csv')
hero_stats = load_data('hero_pick_ban_winrate.csv')
navi_match_history = load_data_history()

# Sidebar
st.sidebar.title("Navigasi Analisis")
page = st.sidebar.radio("Pilih Halaman",
                        ["Ringkasan Tim", "Analisis Pemain [vs ONIC]", "Analisis Pemain [NAVI]", "Analisis Hero",
                         "Rekomendasi Strategis", "All Data"])

# Warna
color_map = {'ONIC ID': '#ffcb00', 'NAVI': '#add8e6'}


# --- Fungsi comparasion chart ---
def create_comparison_chart(df_onic, df_navi, onic_player, navi_player, metric, title):
    onic_val = df_onic[df_onic['Player'] == onic_player][metric].iloc[0]
    navi_val = df_navi[df_navi['Player'] == navi_player][metric].iloc[0]

    # Membuat dataframe kecil untuk plotting
    chart_data = pd.DataFrame({
        'Pemain': [f"{onic_player} (ONIC)", f"{navi_player} (NAVI)"],
        metric: [onic_val, navi_val]
    })

    # Membuat bar chart dengan Plotly
    figure = px.bar(chart_data, x='Pemain', y=metric, title=title,
                    text_auto='.2s', color='Pemain', color_discrete_map={
            f"{onic_player} (ONIC)": color_map['ONIC ID'],
            f"{navi_player} (NAVI)": color_map['NAVI']
        })
    figure.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
    figure.update_layout(showlegend=False, xaxis_title="", yaxis_title=metric)
    st.plotly_chart(figure, use_container_width=True)


team_stats_filtered = team_stats[team_stats['Team Name'].isin(['ONIC ID', 'NAVI'])].copy()
team_stats_filtered = team_stats_filtered.sort_values(by='Team Name', ascending=False)

# ==============================================================================
# --- Halaman 1: Ringkasan Tim ---
# ==============================================================================

if page == "Ringkasan Tim":
    st.title("Ringkasan Performa Tim: Head-to-Head")
    st.markdown("---")

    # --- Sesi 1: Performa Keseluruhan ---
    st.header("Sesi 1: Performa Keseluruhan")
    st.write("Perbandingan *win rate* antara kedua tim.")

    # Funnel Chart
    df_winrate = team_stats_filtered[['Team Name', 'Match Win Rate%', 'Game Win Rate%']].copy()
    df_winrate = df_winrate.melt(id_vars='Team Name', var_name='Type', value_name='Rate')

    fig_funnel = px.funnel(df_winrate, x='Rate', y='Type', color='Team Name',
                           title="Match WR vs Game WR",
                           color_discrete_map=color_map)
    st.plotly_chart(fig_funnel, use_container_width=True)

    with st.expander("Lihat Analisis Performa Keseluruhan"):
        st.write("""
        - **ONIC** unggul secara signifikan dalam Match WR (70%) dan Game WR (61.67%).
        - **NAVI** memiliki WR yang jauh lebih rendah (0% Match, 15.79% Game), menyoroti area perbaikan utama pada eksekusi strategi dan sinergi tim.
        - **Insight:** Perbedaan konsistensi dan kemampuan untuk mengonversi setiap peluang menjadi hasil yang positif.
        """)
    st.markdown("---")

    # --- Sesi 2: Gameplay ---
    st.header("Sesi 2: Analisis Gameplay")

    # Data kedua tim
    onic_stats = team_stats_filtered[team_stats_filtered['Team Name'] == 'ONIC ID'].iloc[0]
    navi_stats = team_stats_filtered[team_stats_filtered['Team Name'] == 'NAVI'].iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("ONIC ID")
        st.markdown("---")
        st.metric(label="Avg Kills per Game", value=f"{onic_stats['Kills per Game']:.2f}",
                  delta=f"{onic_stats['Kills per Game'] - navi_stats['Kills per Game']:.2f} vs NAVI")

        st.metric(label="Avg Deaths per Game", value=f"{onic_stats['Deaths per Game']:.2f}",
                  delta=f"{onic_stats['Deaths per Game'] - navi_stats['Deaths per Game']:.2f} vs NAVI",
                  delta_color="inverse")

        st.metric(label="KDA Ratio", value=f"{onic_stats['KDA']:.2f}",
                  delta=f"{onic_stats['KDA'] - navi_stats['KDA']:.2f} vs NAVI")

        st.metric(label="Team Kill Participation (%)", value=f"{onic_stats['Team Kill Participation%']:.2f}%",
                  delta=f"{onic_stats['Team Kill Participation%'] - navi_stats['Team Kill Participation%']:.2f}% vs NAVI")

    with col2:
        st.subheader("NAVI")
        st.markdown("---")
        st.metric(label="Avg Kills per Game", value=f"{navi_stats['Kills per Game']:.2f}",
                  delta=f"{navi_stats['Kills per Game'] - onic_stats['Kills per Game']:.2f} vs ONIC")

        st.metric(label="Avg Deaths per Game", value=f"{navi_stats['Deaths per Game']:.2f}",
                  delta=f"{navi_stats['Deaths per Game'] - onic_stats['Deaths per Game']:.2f} vs ONIC",
                  delta_color="inverse")

        st.metric(label="KDA Ratio", value=f"{navi_stats['KDA']:.2f}",
                  delta=f"{navi_stats['KDA'] - onic_stats['KDA']:.2f} vs ONIC")

        st.metric(label="Team Kill Participation (%)", value=f"{navi_stats['Team Kill Participation%']:.2f}%",
                  delta=f"{navi_stats['Team Kill Participation%'] - onic_stats['Team Kill Participation%']:.2f}% vs ONIC")

    with st.expander("Lihat Analisis Gameplay"):
        st.write("""
        - **Produktivitas Kill:** ONIC mencetak lebih banyak Kills per Game (13.4) dengan Deaths per Game yang lebih sedikit (11).
        - **Efektivitas:** KDA ONIC (8.36) jauh melampaui NAVI (3.41).
        - **Insight:** NAVI sering terlibat dalam pertarungan (Kill Participation 70.23%) namun tidak efisien, menghasilkan lebih banyak *deaths* dan *trade-off* yang merugikan.
        """)
    st.markdown("---")

    # --- Sesi 3: Kontrol Objektif ---
    st.header("Sesi 3: Kontrol Objektif")

    col1, col2 = st.columns(2)

    with col1:
        # --- Grafik 1: Tornado Chart untuk Control Rate ---
        # Data untuk Tornado Chart
        df_obj_rate = team_stats_filtered.copy()
        onic_turtle_rate = df_obj_rate[df_obj_rate['Team Name'] == 'ONIC ID']['Cryoturtle Control Rate%'].iloc[0]
        navi_turtle_rate = df_obj_rate[df_obj_rate['Team Name'] == 'NAVI']['Cryoturtle Control Rate%'].iloc[0]
        onic_lord_rate = df_obj_rate[df_obj_rate['Team Name'] == 'ONIC ID']['lord Control Rate%'].iloc[0]
        navi_lord_rate = df_obj_rate[df_obj_rate['Team Name'] == 'NAVI']['lord Control Rate%'].iloc[0]

        y_labels_rate = ['Lord Control Rate (%)', 'Turtle Control Rate (%)']
        fig_tornado = go.Figure()
        fig_tornado.add_trace(go.Bar(
            y=y_labels_rate,
            x=[onic_lord_rate, onic_turtle_rate],
            name='ONIC ID',
            orientation='h',
            marker=dict(color=color_map['ONIC ID'])
        ))
        fig_tornado.add_trace(go.Bar(
            y=y_labels_rate,
            x=[-navi_lord_rate, -navi_turtle_rate],
            name='NAVI',
            orientation='h',
            marker=dict(color=color_map['NAVI'])
        ))

        fig_tornado.update_layout(
            title='Kontrol Objektif (%)',
            barmode='relative',
            xaxis_title="Control Rate (%)",
            yaxis_title="",
            bargap=0.4,
            xaxis=dict(
                tickvals=[-75, -50, -25, 0, 25, 50, 75],
                ticktext=['75', '50', '25', '0', '25', '50', '75']
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_tornado, use_container_width=True)

    with col2:
        # --- Grafik 2: Grouped Bar Chart untuk Slain per Game ---
        objective_df = team_stats_filtered[
            ['Team Name', 'Cryoturtle Kill Count per Game', 'Lord Kill Count per Game']].copy()
        objective_df = objective_df.melt(id_vars='Team Name', var_name='Objective', value_name='Count per Game')

        objective_df['Objective'] = objective_df['Objective'].replace({
            'Cryoturtle Kill Count per Game': 'Turtle Slain',
            'Lord Kill Count per Game': 'Lord Slain'
        })

        fig_grouped_bar = px.bar(objective_df, x="Team Name", y="Count per Game", color="Objective",
                                 barmode='group', text_auto='.2f', title="Avg Turtle/Lord per Game")
        fig_grouped_bar.update_layout(xaxis_title="", yaxis_title="Rata-rata per Game", legend_title="Objektif")
        st.plotly_chart(fig_grouped_bar, use_container_width=True)

    tower_df = team_stats_filtered[
        ['Team Name', 'Tower Destroy Count per Game', 'Tower Destroyed Count per Game']].copy()
    tower_df = tower_df.melt(id_vars='Team Name', var_name='Metric', value_name='Count per Game')

    tower_df['Metric'] = tower_df['Metric'].replace({
        'Tower Destroy Count per Game': 'Destroy',
        'Tower Destroyed Count per Game': 'Destroyed'
    })

    fig_tower_bar = px.bar(tower_df, x="Team Name", y="Count per Game", color="Metric",
                           barmode='group', text_auto='.2f',
                           title="Objektif Turret/game",
                           color_discrete_map={
                               'Destroy': 'green',
                               'Destroyed': 'red'
                           })
    fig_tower_bar.update_layout(xaxis_title="", yaxis_title="Avg/game", legend_title="Turret")
    st.plotly_chart(fig_tower_bar, use_container_width=True)

    with st.expander("Lihat Analisis Objektif"):
        st.write("""
        - **Kekuatan di Early Game:** Data menunjukkan NAVI cukup kompetitif dalam perebutan objektif awal (Turtle). Mereka mampu mengamankan rata-rata **1.26 Turtle per game**, angka yang hampir menyamai ONIC (1.4 per game). Ini menandakan bahwa strategi dan koordinasi mereka untuk 10 menit pertama permainan sudah cukup solid.

        - **Problem Transisi ke Late Game:** Namun, kekuatan ini tidak berlanjut. Terlihat adanya penurunan performa yang drastis saat game beralih ke perebutan Lord. NAVI hanya mampu mengamankan **0.42 Lord per game**, sangat jauh di bawah ONIC yang dominan dengan 1.12 Lord per game.

        - **Kontrol Map (Turret):** NAVI kehilangan rata-rata **7.21 turret per game**, sementara hanya mampu menghancurkan **3.34 turret** milik lawan. Perbedaan signifikan ini menunjukkan bahwa mereka terus-menerus kehilangan kontrol *map* dan berada di bawah tekanan.

        - **Insight Utama:** Pola ini mengindikasikan bahwa NAVI seringkali **kehilangan arah dan momentum setelah fase Turtle berakhir**. Mereka tampak kesulitan dalam **transisi strategi dari mid-game ke late-game**. Kegagalan mengontrol Lord secara konsisten inilah yang menjadi salah satu penyebab utama mereka kehilangan kontrol *map* dan akhirnya kalah dalam pertandingan.
        """)
    st.markdown("---")

    # --- Sesi 4: Ringkasan Analisis---
    st.header("Ringkasan Analisis")
    st.success(
        """
        **Kesimpulan Utama:**
        1.  **Core Problem:** Masalah utama NAVI berakar pada **efektivitas team fight yang rendah** (KDA rendah walaupun Kill Participation tinggi) dan **kegagalan mengamankan objektif krusial (terutama Lord)**.
        2.  **Siklus Negatif:** Dua masalah ini menciptakan siklus: Gagal mengontrol objektif -> kalah gold/level -> kalah team fight -> semakin sulit mengontrol objektif.

        **Selanjutnya:** Analisis pada level **Pemain** dan **Hero** akan bertujuan untuk mengidentifikasi area yang menjadi penyebab dari masalah-masalah ini.
        """
    )
# ==============================================================================
# --- Halaman 2: Analisis Pemain ---
# ==============================================================================

if page == "Analisis Pemain [vs ONIC]":
    st.title("Analisis Pemain")
    st.markdown("---")

    # --- 1. Jungler: Kairi (ONIC) vs Woshipaul (NAVI) ---
    st.subheader("Jungler: Kairi (ONIC) vs Woshipaul (NAVI)")
    st.markdown(
        "Fokus analisis pada efisiensi *farming*, efektivitas war, dan kemampuan mengamankan objektif krusial.")

    col1, col2 = st.columns(2)
    with col1:
        kairi_lord_pg = onic_player_stats[onic_player_stats['Player'] == 'Kairi']['Lord Secured'].iloc[0] / \
                        onic_player_stats[onic_player_stats['Player'] == 'Kairi']['Games Played'].iloc[0]
        woshipaul_lord_pg = navi_player_stats[navi_player_stats['Player'] == 'Woshipaul']['Lord Secured'].iloc[0] / \
                            navi_player_stats[navi_player_stats['Player'] == 'Woshipaul']['Games Played'].iloc[0]

        # Membuat DataFrame untuk chart
        chart_data_lord = pd.DataFrame({
            'Pemain': ['Kairi (ONIC)', 'Woshipaul (NAVI)'],
            'Lord Secured per Game': [kairi_lord_pg, woshipaul_lord_pg]
        })

        # Membuat Bar Chart
        fig_lord = px.bar(chart_data_lord, x='Pemain', y='Lord Secured per Game',
                          title='Avg Lord/game', text_auto='.2f', color='Pemain',
                          color_discrete_map={'Kairi (ONIC)': color_map['ONIC ID'],
                                              'Woshipaul (NAVI)': color_map['NAVI']})
        fig_lord.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
        fig_lord.update_layout(showlegend=False, xaxis_title="", yaxis_title="Lord/Game")
        st.plotly_chart(fig_lord, use_container_width=True)

    with col2:
        # Menghitung metrik Turtle per game
        kairi_turtle_pg = onic_player_stats[onic_player_stats['Player'] == 'Kairi']['Cryoturtle Secured'].iloc[0] / \
                          onic_player_stats[onic_player_stats['Player'] == 'Kairi']['Games Played'].iloc[0]
        woshipaul_turtle_pg = navi_player_stats[navi_player_stats['Player'] == 'Woshipaul']['Cryoturtle Secured'].iloc[
                                  0] / \
                              navi_player_stats[navi_player_stats['Player'] == 'Woshipaul']['Games Played'].iloc[0]

        # Membuat DataFrame untuk chart
        chart_data_turtle = pd.DataFrame({
            'Pemain': ['Kairi (ONIC)', 'Woshipaul (NAVI)'],
            'Turtle Secured per Game': [kairi_turtle_pg, woshipaul_turtle_pg]
        })

        # Membuat Bar Chart
        fig_turtle = px.bar(chart_data_turtle, x='Pemain', y='Turtle Secured per Game',
                            title='Avg Turtle/game', text_auto='.2f', color='Pemain',
                            color_discrete_map={'Kairi (ONIC)': color_map['ONIC ID'],
                                                'Woshipaul (NAVI)': color_map['NAVI']})
        fig_turtle.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
        fig_turtle.update_layout(showlegend=False, xaxis_title="", yaxis_title="Turtle/Game")
        st.plotly_chart(fig_turtle, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Kairi', 'Woshipaul', 'KDA Ratio',
                                'KDA')

    with col4:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Kairi', 'Woshipaul', 'Gold Per Minute',
                                'GPM')

    with st.expander("Lihat Analisis Jungler"):
        st.write("""
        - **KDA:** Perbedaan paling signifikan terletak pada KDA, di mana Kairi (6.93) unggul jauh atas Woshipaul (2.60). Angka KDA yang tinggi ini menunjukkan bahwa Kairi tidak hanya agresif, tetapi juga sangat efektif. Kairi secara konsisten terlibat dalam eliminasi lawan tanpa harus sering mati. Ini mengindikasikan pengambilan keputusan, posisi, dan eksekusi yang baik.
        
        - **Lord:** Avg **1.0 Lord per game** yang diamankan oleh Kairi menunjukkan bahwa ia adalah eksekutor saat permainan berada di fase paling menentukan. Sebaliknya, angka 0.33 Lord per game untuk Woshipaul menyoroti kesulitan dalam kontes objektif ini.
        
        - **Insight Utama:** Perbedaan ini menciptakan dua narasi yang berbeda. Kairi menggunakan efisiensi war dan GPM-nya yang tinggi untuk dikonversi menjadi kontrol objektif (Lord) untuk memastikan kemenangan. Sementara itu, Woshipaul seringkali harus bertarung dari posisi yang kurang menguntungkan, membuat perebutan Lord yang berisiko tinggi menjadi sulit untuk dimenangkan.
        """)
    st.markdown("---")

    # --- 2. Gold Laner: Savero (ONIC) vs Xyve (NAVI) ---
    st.subheader("Gold Laner: Savero (ONIC) vs Xyve (NAVI)")
    st.markdown("Fokus analisis pada efisiensi *farming*, output *damage*, dan push turret.")

    chart_col1, chart_col2, chart_col3 = st.columns(3)
    with chart_col1:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Savero', 'Xyve', 'Gold Per Minute',
                                'GPM')
    with chart_col2:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Savero', 'Xyve', 'Damage Per Minute',
                                'DPM')
    with chart_col3:
        # Building Damage Share
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Savero', 'Xyve', 'Building Damage Share%',
                                'Push Turret (Share) %')

    with st.expander("Lihat Analisis Gold Laner"):
        st.write("""
        - Savero adalah **Team-Fight Carry** yang unggul dalam GPM (781) dan DPM (3244).
        - Dengan GPM dan DPM sedikit dibawah Savero, Xyve adalah karyawan **PT Bongkar Turret**. Kontribusinya pada `Building Damage Share%` sebesar **69.38%** merupakan *win condition* alternatif yang potensial bagi NAVI.
        - **Insight:** Jika NAVI tidak bisa memenangkan pertarungan 5v5 secara langsung, strategi yang berfokus melindungi dan memfasilitasi Xyve untuk melakukan *split push* adalah cara yang paling realistis untuk meraih kemenangan.
        """)
    st.markdown("---")

    # --- 3. Mid Laner: S A N Z (ONIC) vs xMagic (NAVI) ---
    st.subheader("Mid Laner: S A N Z (ONIC) vs xMagic (NAVI)")
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    with chart_col1:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'S A N Z', 'xMagic', 'KDA Ratio',
                                'KDA')
    with chart_col2:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'S A N Z', 'xMagic', 'Kill Participation%',
                                'Kill Participation %')
    with chart_col3:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'S A N Z', 'xMagic', 'Damage Share%',
                                'Damage Share %')
    with st.expander("Lihat Analisis Mid Laner"):
        st.write("""
        - Kedua pemain memiliki `Kill Participation%` yang hampir sama (~80%), menandakan peran sentral mereka dalam tim.
        - **Efisiensi:** S A N Z (ONIC) jauh lebih efisien dengan KDA 6.63, dibandingkan xMagic (NAVI) dengan KDA 3.65.
        - **Insight:** Mid laner NAVI perlu meningkatkan *survivability* dan pengambilan keputusan untuk hasil yang lebih positif.
        """)
    st.markdown("---")

    # --- 4. Roamer: Kiboy (ONIC) vs Karss (NAVI) ---
    st.subheader("Roamer: Kiboy (ONIC) vs Karss (NAVI)")
    st.markdown("Fokus pada kemampuan *playmaking* dan *crowd control*.")
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    with chart_col1:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Kiboy', 'Karss', 'Average Assists',
                                'Avg Assists per Game')
    with chart_col2:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Kiboy', 'Karss', 'Damage Taken Per Minute',
                                'Damage Taken / Min')
    with chart_col3:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Kiboy', 'Karss', 'Control time per game/s',
                                'Avg Control Time / Game (s)')
    with st.expander("Lihat Analisis Roamer"):
        st.write("""
        - **Playmaking & CC:** Kiboy (ONIC) unggul dalam jumlah assist per game (7.85). Perbedaan juga terlihat pada `Control time per game/s`, di mana Kiboy (17.32s) sekitar 13.7% lebih efektif dibandingkan Karss (15.23s) dalam mengunci pergerakan lawan.
        - **Insight:** Meskipun selisihnya tidak sebesar yang diperkirakan, kemampuan *crowd control* Kiboy yang secara konsisten sedikit lebih unggul ini tetap menjadi kunci yang membuka peluang bagi timnya. Setiap detik dalam melakukan CC kepada lawan sangat berharga dalam pertarungan tim tingkat.
        """)
    st.markdown("---")

    # --- 5. EXP Laner: Lutpiii (ONIC) vs bq syaii (NAVI) ---
    st.subheader("EXP Laner: Lutpiii (ONIC) vs bq syaii (NAVI)")
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    with chart_col1:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Lutpiii', 'bq syaii', 'KDA Ratio',
                                'KDA')
    with chart_col2:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Lutpiii', 'bq syaii', 'Average Deaths',
                                'Avg Deaths / game')
    with chart_col3:
        create_comparison_chart(onic_player_stats, navi_player_stats, 'Lutpiii', 'bq syaii', 'Damage Taken Share%',
                                'Damage Taken Share %')
    with st.expander("Lihat Analisis EXP Laner"):
        st.write("""
        - **Stabilitas:** Lutpiii (ONIC) menunjukkan performa yang jauh lebih stabil dengan rata-rata kematian yang rendah (2.9 per game) dan KDA yang solid (3.12).
        - **Titik Lemah NAVI:** EXP Lane NAVI adalah *weak point*. *Avg deaths* bq syaii yang tinggi (4.38 per game) dan KDA yang sangat rendah (1.07) menunjukkan ia sering menjadi target eksploitasi lawan.
        - **Insight:** EXP Lane NAVI bisa menjadi salah satu 'pintu masuk' bagi keunggulan lawan. Memperkuat lane ini melalui *draft* hero yang lebih *sustain* atau rotasi yang lebih baik mungkin bisa membantu.
        """)
    st.markdown("---")

    st.header("Ringkasan Analisis Pemain & Implikasi Strategis")
    st.info(
        """
        **Kekuatan NAVI yang Teridentifikasi:**
        - **Gold Lane (Xyve):** Hyper carry, saangat bagus dalam *push turret* dengan potensi sebagai *win condition*.
        - **Early Game (Jungler):** Mampu bersaing dalam perebutan Turtle di awal game.

        **Kelemahan Kritis NAVI:**
        1.  **Kontrol Objektif Late Game (Jungler):** Kurang dalam hal mengamankan Lord per game.
        2.  **EXP Lane:** Sering menjadi titik eksploitasi lawan dengan *avg deaths* tertinggi.
        3.  **Efisiensi (Mid & Roamer):** Kurang efektif dalam konversi aksi menjadi hasil (KDA rendah, *control time* lebih rendah).

        **Rekomendasi:** NAVI harus fokus pada koordinasi tim dan pengambilan keputusan yang matang pada fase krusial.
        """
    )

if page == "Analisis Pemain [NAVI]":
    st.title("Analisis Pemain NAVI")
    st.info(
        "Analisis ini membandingkan pemain yang pernah mengisi role Jungler, EXP, dan Roam di NAVI selama MPL S15, berdasarkan statistik individu dan hasil pertandingan saat mereka bermain.")
    st.markdown("---")

    # ==============================================================================
    # --- Analisis 1: Jungler (Aether vs Woshipaul) ---
    # ==============================================================================
    st.header("Analisis Jungler: Aether vs Woshipaul")
    st.markdown(
        "Fokus analisis pada *winning impact* dan kontribusi damage.")

    # Data Prep
    aether_stats = navi_player_stats[navi_player_stats['Player'] == 'Aether'].iloc[0]
    woshipaul_stats = navi_player_stats[navi_player_stats['Player'] == 'Woshipaul'].iloc[0]

    # Metrik Kunci
    aether_wins = aether_stats['Number of game wins']
    woshipaul_wins = woshipaul_stats['Number of game wins']
    aether_dpm = aether_stats['Damage Per Minute']
    woshipaul_dpm = woshipaul_stats['Damage Per Minute']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Aether")
        st.image("images/Aether.png", width=250)

        st.metric("Total Games Won (from 17 games)", f"{aether_wins} Game",
                  delta=f"{aether_wins - woshipaul_wins} Game vs Woshipaul")
        st.metric("Damage Per Minute (DPM)", f"{int(aether_dpm)}",
                  delta=f"{int(aether_dpm - woshipaul_dpm)} vs Woshipaul")

        st.markdown("---")
        st.write(f"**KDA:** {aether_stats['KDA Ratio']:.2f}")
        st.write(f"**Avg Deaths:** {aether_stats['Average Deaths']:.2f}")

    with col2:
        st.subheader("Woshipaul")
        st.image("images/Woshipaul.png", width=250)

        st.metric("Total Games Won (from 21 games)", f"{woshipaul_wins} Game",
                  delta=f"-{aether_wins - woshipaul_wins} Game vs Aether")
        st.metric("Damage Per Minute (DPM)", f"{int(woshipaul_dpm)}",
                  delta=f"-{int(aether_dpm - woshipaul_dpm)} vs Aether")

        st.markdown("---")
        st.write(f"**KDA:** {woshipaul_stats['KDA Ratio']:.2f}")
        st.write(f"**Avg Deaths:** {woshipaul_stats['Average Deaths']:.2f}")

    with st.expander("Lihat Analisis Jungler"):
        st.write("""
        #### 1. Impact Kemenangan
        Data menunjukkan Aether secara langsung berkontribusi pada **4 kemenangan game**, sementara Woshipaul berkontribusi pada **2 kemenangan game**. Ini mengindikasikan bahwa gaya bermain Aether memiliki korelasi **dua kali lebih tinggi** untuk membawa tim meraih kemenangan dalam sebuah game.

        #### 2. Damage Output
        Di sini Aether unggul secara signifikan:
        - **Damage Per Minute (DPM) Aether:** 2253.24
        - **Damage Per Minute (DPM) Woshipaul:** 1816.29

        Aether memberikan kerusakan **sekitar 24% lebih banyak per menitnya**. Ini membuktikan bahwa Aether adalah Jungler yang lebih agresif dan lebih efektif dalam menekan lawan di dalam pertarungan tim. Hal ini juga dikarenakan Hero pool yang digunakan olehnya mayoritas adalaah Assassin/Fighter. Berbeda dengan Woshipaul, selain bermain Assassin/Fighter dia juga bermain Tank Jungler.

        ---

        **Kesimpulan:**
        Meskipun Woshipaul lebih sustain (lower death avg), kelebihan Aether terletak pada **kemampuannya yang terbukti lebih sering memenangkan game** dan **perannya sebagai damage dealer**.
        """)
    st.markdown("---")

    # ==============================================================================
    # --- Analisis 2: EXP Laner (Karss vs bq syaii vs Febbb) ---
    # ==============================================================================
    st.header("Analisis EXP Laner")

    # Data Prep
    karss_stats = navi_player_stats[navi_player_stats['Player'] == 'Karss'].iloc[0]
    bq_syaii_stats = navi_player_stats[navi_player_stats['Player'] == 'bq syaii'].iloc[0]
    febbb_stats = navi_player_stats[navi_player_stats['Player'] == 'Febbb'].iloc[0]

    karss_exp_matches = navi_match_history[navi_match_history['Player_Exp'].str.contains('Karss')]
    bq_syaii_matches = navi_match_history[navi_match_history['Player_Exp'].str.contains('bq syaii')]
    febbb_matches = navi_match_history[navi_match_history['Player_Exp'].str.contains('Febbb')]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Karss")
        st.image("images/Karss.png", width=250)
        st.metric("Games Won as EXP (from 15 games)", f"{karss_exp_matches['Score_NAVI'].sum()} Game")
        st.write(f"**WR: 20.0%%**")
        st.write(f"**KDA Ratio:** {karss_stats['KDA Ratio']:.2f} (all role)")
        st.write(f"**Avg Deaths:** {karss_stats['Average Deaths']:.2f}")

    with col2:
        st.subheader("bq syaii")
        st.image("images/bq syaii.png", width=250)
        st.metric("Games Won as EXP (from 16 games)", f"{bq_syaii_matches['Score_NAVI'].sum()} Game")
        st.write(f"**WR: 12.5%**")
        st.write(f"**KDA Ratio:** {bq_syaii_stats['KDA Ratio']:.2f}")
        st.write(f"**Avg Deaths:** {bq_syaii_stats['Average Deaths']:.2f}")

    with col3:
        st.subheader("Febbb")
        st.image("images/Febbb.png", width=250)
        st.metric("Games Won as EXP (from 7 games)", f"{febbb_matches['Score_NAVI'].sum()} Game")
        st.write(f"**WR: 14.3%**")
        st.write(f"**KDA Ratio:** {febbb_stats['KDA Ratio']:.2f}")
        st.write(f"**Avg Deaths:** {febbb_stats['Average Deaths']:.2f}")

    with st.expander("Lihat Analisis EXP Laner"):
        st.write("""
        - Dilihat dari rata-rata kematian, Karss (3.63) dan Febbb (4.00) menunjukkan tingkat kematian yang lebih rendah dibandingkan bq syaii (4.38). Ini mengindikasikan Karss lebih sulit untuk ditaklukkan di lane.
        - Karss memiliki KDA tertinggi (1.79), diikuti oleh Febbb (1.39) dan bq syaii (1.07).
        - NAVI meraih 3 kemenangan game saat Karss bermain sebagai EXP Laner. Saat bq syaii bermain, mereka meraih 2 kemenangan game. Dan saat Febbb bermain, mereka meraih 1 kemenangan game.
        - **Kesimpulan Awal:** Karss memberikan stabilitas dan efisiensi tertinggi di EXP Lane. Meskipun ia kemudian pindah ke role Roamer, performanya sebagai EXP Laner adalah yang paling solid di antara ketiganya.
        """)
    st.markdown("---")

    # ==============================================================================
    # --- Analisis 3: Roamer (Hanafi vs Karss) ---
    # ==============================================================================
    st.header("Analisis Roamer")

    # Data Prep
    hanafi_stats = navi_player_stats[navi_player_stats['Player'] == 'Hanafi'].iloc[0]
    # Karss stats sudah di-load sebelumnya

    hanafi_roam_matches = navi_match_history[navi_match_history['Player_Roam'].str.contains('Hanafi')]
    karss_roam_matches = navi_match_history[navi_match_history['Player_Roam'].str.contains('Karss')]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hanafi")
        st.image("images/Hanafi.png", width=250)
        st.metric("Games Won as Roamer (from 15 games)", f"{hanafi_roam_matches['Score_NAVI'].sum()} Game")
        st.write(f"**WR: 20.0%**")
        st.write(f"**KDA Ratio:** {hanafi_stats['KDA Ratio']:.2f}")
        st.write(f"**Average Assists:** {hanafi_stats['Average Assists']:.2f}")
        st.write(f"**Control time per game/s:** {hanafi_stats['Control time per game/s']:.2f}s")

    with col2:
        st.subheader("Karss")
        st.image("images/Karss.png", width=250)
        st.metric("Games Won as Roamer (from 23 games)", f"{karss_roam_matches['Score_NAVI'].sum()} Game")
        st.write(f"**WR: 13.0%**")
        st.write(f"**KDA Ratio:** {karss_stats['KDA Ratio']:.2f}  (all role)")
        st.write(f"**Average Assists:** {karss_stats['Average Assists']:.2f}")
        st.write(f"**Control time per game/s:** {karss_stats['Control time per game/s']:.2f}s")

    with st.expander("Lihat Analisis Roamer"):
        st.write("""
        - **Playmaking & Efisiensi:** Statistik individu menunjukkan keunggulan Hanafi. Dia memiliki rata-rata assist per game yang lebih tinggi (6.67) dibandingkan Karss (5.47) dan juga KDA yang lebih baik (2.05 vs 1.79).

        - **Inisiasi Pertarungan:** Di sisi lain, Karss unggul dalam durasi *crowd control* per game (15.23 detik) dibandingkan Hanafi (12.72 detik), yang mengindikasikan kemampuan inisiasi yang lebih kuat untuk memulai pertarungan.

        - **Dampak Kemenangan (Win Rate):** Ini adalah pembeda paling signifikan. Meskipun keduanya sama-sama meraih 3 kemenangan game, Hanafi mencapainya hanya dalam 15 game (**Win Rate 20.0%**), sementara Karss membutuhkan 23 game (**Win Rate 13.0%**). Data ini menunjukkan bahwa peluang tim untuk menang secara statistik lebih tinggi saat Hanafi bermain sebagai Roamer.

        - **Kesimpulan:** Meskipun Karss memberikan durasi inisiasi yang lebih lama, efektivitas dan dampak Hanafi terhadap kemenangan tim jauh lebih unggul. Dengan KDA, assist, dan terutama **Win Rate yang lebih tinggi**, Hanafi terbukti menjadi pilihan Roamer yang lebih solid dan lebih efektif untuk NAVI.
        """)
    st.markdown("---")

    # ==============================================================================
    # --- Kesimpulan ---
    # ==============================================================================
    st.header("Kesimpulan")
    st.success(
        """
        Berdasarkan analisis statistik dan konteks pertandingan, berikut adalah rekomendasi roster NAVI untuk mencapai performa yang lebih kompetitif:
        - **Jungler: AETHER**
          - **Alasan:** Terbukti menyumbangkan lebih banyak kemenangan game dan menunjukkan KDA yang sedikit lebih baik. Gaya bermainnya terbukti mampu membawa tim ke pertandingan yang lebih sengit (skor 1-2).
        - **EXP Lane: KARSS**
          - **Alasan:** Sebelum berpindah role, Karss adalah EXP Laner yang paling stabil dengan KDA tertinggi dan rata-rata kematian yang lebih rendah. Mengembalikannya ke posisi ini dapat memperkuat Sidelane NAVI yang sering menjadi titik lemah.
        - **Roamer: HANAFI**
          - **Alasan:** Meskipun Karss memiliki *crowd control* yang baik, KDA dan rata-rata assist Hanafi yang lebih tinggi menunjukkan ia dapat menciptakan peluang bagi tim dengan risiko yang lebih kecil. Jika Karss kembali ke EXP Lane, Hanafi adalah pilihan Roamer yang paling solid.

        **Roster Potensial Terbaik:** (Sama seperti Roster di 2 Match Pembuka NAVI di MPL S15)
        - **Jungler:** Aether
        - **EXP Lane:** Karss
        - **Roamer:** Hanafi
        - **Mid Lane:** xMagic
        - **Gold Lane:** Xyve

        Kombinasi ini memberikan keseimbangan antara stabilitas di lane (Karss), potensi *playmaking* (Hanafi), dan kemampuan Jungler untuk mengamankan game (Aether).
        """
    )

# ==============================================================================
# --- Halaman 4: Analisis Hero ---
# ==============================================================================

if page == "Analisis Hero":
    meta_hero_stats = hero_stats.copy()
    meta_hero_stats['Contest Count'] = meta_hero_stats['Pick'] + meta_hero_stats['Ban']

    st.title("Analisis Hero")
    st.markdown(
        "Menganalisis prioritas drafting tim dengan membandingkannya terhadap meta keseluruhan MPL ID Season 15.")
    st.markdown("---")

    # --- Sesi 1: Meta Snapshot MPL Season 15 ---
    st.header("1. Meta Snapshot: Hero Terkuat di MPL S15")
    st.markdown(
        "Hero yang paling mendominasi fase draft, diukur dari total Pick+Ban dan Win Rate.")

    col1, col2 = st.columns(2)
    with col1:
        # Top 10 Paling Diperebutkan berdasarkan jumlah absolut Pick + Ban
        top_contested = meta_hero_stats.nlargest(10, 'Contest Count')
        fig = px.bar(top_contested, x='Contest Count', y='Hero', orientation='h',
                     title='Top 10 Hero Paling Diperebutkan (Total Pick+Ban)',
                     text_auto=True, color='Contest Count', color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title="Total Pick + Ban")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # Top 10 Win Rate Tertinggi (dengan minimal pick yang relevan)
        min_picks = 20  # Filter untuk hero yang cukup sering muncul agar WR relevan
        top_winrate = meta_hero_stats[meta_hero_stats['Pick'] > min_picks].nlargest(10, 'Win Rate%')
        fig = px.bar(top_winrate, x='Win Rate%', y='Hero', orientation='h',
                     title=f'Top 10 Hero Win Rate Tertinggi (Min. {min_picks} Picks)',
                     text_auto='.2f', color='Win Rate%', color_continuous_scale='Greens')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    st.info(
        """
        Hero seperti **Harith, Granger, dan Fanny** adalah prioritas utama dalam draft (paling sering di-pick/ban). 
        Sementara itu, hero seperti **Suyou, Pharsa, dan Gloo** terbukti menjadi pilihan yang sangat efektif dan memiliki persentase kemenangan tertinggi di antara hero-hero yang sering dimainkan.
        """
    )
    st.markdown("---")

    # --- Sesi 2: Analisis Prioritas Pick ---
    st.header("2. Analisis Prioritas Pick")
    st.markdown(
        "Membandingkan frekuensi pick hero oleh tim dengan popularitas hero tersebut di MPL (Total Pick+Ban). **Ukuran gelembung menunjukkan Win Rate tim dengan hero tersebut.**")

    # Menggabungkan data tim dengan data meta
    onic_merged = pd.merge(onic_hero_stats, meta_hero_stats[['Hero', 'Contest Count']], on='Hero', how='left')
    navi_merged = pd.merge(navi_hero_stats, meta_hero_stats[['Hero', 'Contest Count']], on='Hero', how='left')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Prioritas Pick ONIC")
        onic_top_picks = onic_merged.nlargest(10, 'Pick Count')
        fig = px.scatter(onic_top_picks, x='Pick Count', y='Contest Count',
                         size='Game Win Rate%', color='Hero',
                         title='Pick ONIC vs. Popularitas Meta',
                         hover_name='Hero', size_max=40,
                         labels={'Pick Count': 'Jumlah Pick oleh ONIC',
                                 'Contest Count': 'Popularitas di MPL (Total Pick+Ban)'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Prioritas Pick NAVI")
        navi_top_picks = navi_merged.nlargest(10,
                                              'Pick Count').copy()

        navi_top_picks['Bubble Size'] = navi_top_picks['Game Win Rate%']
        navi_top_picks.loc[navi_top_picks['Bubble Size'] == 0, 'Bubble Size'] = 1

        fig = px.scatter(navi_top_picks, x='Pick Count', y='Contest Count',
                         size='Bubble Size',
                         color='Hero',
                         title='Pick NAVI vs. Popularitas Meta',
                         hover_name='Hero',

                         hover_data={
                             'Bubble Size': False,
                             'Game Win Rate%': True
                         },
                         size_max=40,
                         labels={'Pick Count': 'Jumlah Pick oleh NAVI',
                                 'Contest Count': 'Popularitas di MPL (Total Pick+Ban)'})
        # ==========================================================

        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Lihat Analisis Prioritas Pick"):
        st.write("""
        - **ONIC:** Mengikuti meta dan mampu mengeksekusinya dengan baik. Mereka memprioritaskan hero populer seperti **Badang** dan **Harith**, dan ukuran lingkaran yang besar menunjukkan bahwa mereka memiliki Win Rate yang tinggi saat menggunakan hero tersebut.

        - **NAVI:** Mengikuti meta dengan baik dengan ikut memprioritaskan **Kalea** (10 picks), salah satu hero yang paling sering diperebutkan di MPL. Namun, masalah utamanya terlihat jelas: **meskipun memilih hero meta yang kuat, performa mereka jauh di bawah standar.** Win Rate NAVI yang hanya 30%.

        - **Insight:** Masalah NAVI bukan pada *pick* hero yang salah, tetapi pada **eksekusi strategi saat menggunakan hero meta yang kuat.** Ketergantungan pada Kalea menjadi bumerang karena tidak mampu mengkonversinya menjadi kemenangan. Hal ini juga diperparah dengan kegagalan pada hero meta lain seperti **Joy** dan **Zhuxin** (0% Win Rate), yang menunjukkan adanya masalah pada eksekusi.
        """)

    # --- Sesi 3: Analisis Efektivitas Signature Hero ---
    st.header("3. Efektivitas Signature Hero")

    hero_onic = 'Badang'
    hero_navi = 'Kalea'

    onic_hero_perf = onic_merged[onic_merged['Hero'] == hero_onic].iloc[0]
    meta_hero_perf_onic = meta_hero_stats[meta_hero_stats['Hero'] == hero_onic].iloc[0]

    navi_hero_perf = navi_merged[navi_merged['Hero'] == hero_navi].iloc[0]
    meta_hero_perf_navi = meta_hero_stats[meta_hero_stats['Hero'] == hero_navi].iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{hero_onic} ONIC")
        st.metric(f"Win Rate {hero_onic} ONIC", f"{onic_hero_perf['Game Win Rate%']:.1f}%",
                  f"{onic_hero_perf['Game Win Rate%'] - meta_hero_perf_onic['Win Rate%']:.1f}% vs Avg MPL")
        st.metric(f"KDA {hero_onic} ONIC", f"{onic_hero_perf['KDA']:.2f}")

    with col2:
        st.subheader(f"{hero_navi} NAVI")
        st.metric(f"Win Rate {hero_navi} NAVI", f"{navi_hero_perf['Game Win Rate%']:.1f}%",
                  f"{navi_hero_perf['Game Win Rate%'] - meta_hero_perf_navi['Win Rate%']:.1f}% vs Avg MPL")
        st.metric(f"KDA {hero_navi} NAVI", f"{navi_hero_perf['KDA']:.2f}")

    with st.expander("Lihat Analisis Efektivitas"):
        st.write(f"""
        - **ONIC & {hero_onic}:** Win Rate mereka ({onic_hero_perf['Game Win Rate%']:.1f}%) **jauh di atas** rata-rata liga ({meta_hero_perf_onic['Win Rate%']:.1f}%). Ini adalah hero fleksibel untuk Roam/EXP yang harus diwaspadai.
        - **NAVI & {hero_navi}:** Performa NAVI dengan {hero_navi} lebih buruk dari rata-rata MPL. Win Rate mereka ({navi_hero_perf['Game Win Rate%']:.1f}%) masih di bawah rata-rata ({meta_hero_perf_navi['Win Rate%']:.1f}%).
        """)
    st.markdown("---")

    # --- Sesi 4: Rekomendasi Draft Strategis ---
    st.header("4. Rekomendasi Draft (S15)")
    st.success(
        """
        **Prioritas Pick untuk NAVI:**
        1.  **Ambil Hero Meta yang Kuat:** Prioritaskan hero-hero dari chart "Top 10 Win Rate Tertinggi" yang lolos dari fase ban. Mengamankan hero yang secara statistik memiliki peluang menang lebih tinggi adalah langkah logis.
        2.  **Pelajari & Adaptasi:** NAVI harus mulai melatih hero-hero meta (yang ada di kanan atas chart pertama) untuk memperluas *hero pool*.
        """
    )

# ==============================================================================
# --- Halaman 5: Rekomendasi Strategis ---
# ==============================================================================

if page == "Rekomendasi Strategis":
    st.title("Rekomendasi Strategis")
    st.markdown("---")

    st.header("Data #1: Dominasi Gold Laner")
    st.markdown(
        """
        Xyve bukanlah sekadar pemain yang bagus, dia adalah pemain terbaik di tim NAVI.
        """
    )
    # Visualisasi data Xyve
    col1, col2, col3, col4 = st.columns(4)
    xyve_stats = navi_player_stats[navi_player_stats['Player'] == 'Xyve'].iloc[0]
    col1.metric("KDA Ratio (Peringkat #1 di Tim)", f"{xyve_stats['KDA Ratio']:.2f}")
    col2.metric("Damage/Minute (Peringkat #1 di Tim)", f"{int(xyve_stats['Damage Per Minute'])}")
    col3.metric("Avg Kills/Game (Peringkat #1 di Tim)", f"{xyve_stats['Average Kills per game']:.2f}")
    col4.metric("Avg Deaths/Game (Peringkat #1 di Tim)", f"{xyve_stats['Average Deaths']:.2f}", delta_color="inverse")

    st.markdown(
        """
        Memiliki satu pemain yang unggul secara statistik di semua lini (damage, efisiensi, dan survivability) berarti tim memiliki sebuah 'Asuransi Kemenangan'. Semakin lama permainan berlangsung, semakin besar kemungkinan Xyve untuk membawa tim menuju kemenangan. Ini melahirkan...
        """
    )
    st.subheader("Playbook 1: 'Late Game Insurance'")
    st.info(
        """
        - **Kapan Digunakan:** Saat draft lawan kuat di *early game* atau saat NAVI mendapatkan hero *late-game*. Ini adalah strategi untuk 'memperlambat' tempo permainan.
        - **Fokus Draft:** Pilih hero yang bisa menahan gempuran dan membersihkan *wave minion* dengan cepat (misalnya Pharsa). Di EXP lane, butuh hero yang sangat mandiri dan sulit ditumbangkan.
        - **Eksekusi Gameplay:** Prioritaskan farming untuk Xyve. Hindari pertarungan yang tidak perlu sebelum Xyve mendapatkan item kuncinya. Tujuannya adalah membawa permainan ke menit 12+, di mana Xyve bisa menjadi *damage dealer* yang mematikan atau melakukan *split push* yang merepotkan lawan.
        """
    )
    st.markdown("---")

    st.header("Data #2: Agresivitas Jungler")
    st.markdown(
        """
        Meskipun tidak se-efisien Woshipaul dalam survive, gaya bermain agresif Aether terbukti lebih sering menghasilkan kemenangan game.
        """
    )
    # Visualisasi perbandingan jungler
    col1, col2 = st.columns(2)
    aether_stats = navi_player_stats[navi_player_stats['Player'] == 'Aether'].iloc[0]
    col1.metric("Games won by Aether", f"{aether_stats['Number of game wins']} Game", "2x Lebih Banyak")
    col2.metric("Damage Per Minute Aether", f"{int(aether_stats['Damage Per Minute'])}", "~24% Lebih Tinggi")

    st.markdown(
        """
        Data ini menunjukkan bahwa NAVI memiliki kemampuan untuk bermain dengan tempo tinggi. Kontribusi *damage* Aether yang besar mampu menciptakan tekanan di awal hingga pertengahan permainan. Ketika NAVI ingin bermain proaktif dan tidak hanya bereaksi, mereka memiliki pemain yang tepat untuk memimpin serangan.
        """
    )
    st.subheader("Playbook 2: 'Early Tempo & Team Fight'")
    st.warning(
        """
        - **Kapan Digunakan:** Saat NAVI berhasil mendapatkan draft hero yang kuat di *early-mid game* (hero *pick-off* atau *burst damage*).
        - **Fokus Draft:** Dukung agresivitas Aether. Pilih Roamer inisiator (seperti Kalea, Badang) dan Mid Laner dengan *follow-up* yang cepat.
        - **Eksekusi Gameplay:** Jadikan Turtle pertama sebagai prioritas. Gunakan keunggulan tempo dari Turtle untuk melakukan invasi, memaksakan pertarungan, dan menghancurkan turret luar. Tujuannya adalah menciptakan efek *snowball*.
        """
    )
    st.markdown("---")

    st.header("Kesimpulan")
    st.success(
        """

        **1. Unpredictable Team:**
        Dengan dua *playbook* yang jelas, agresi cepat melalui **'Early Tempo & Team Fight'** atau kesabaran melalui **'Late Game Insurance'**—NAVI tidak lagi menjadi tim yang mudah dibaca. Lawan harus bersiap menghadapi dua skenario yang sangat berbeda.

        **2. Adaptif saat Fase Draft:**
        NAVI kini dapat memilih *playbook* mereka berdasarkan komposisi hero yang didapat dan yang dimiliki lawan. Melawan tim *late-game*? Jalankan 'Early Tempo'. Melawan tim agresif? Serap tekanan dengan 'Late Game Insurance'.

        **3. Solusi untuk 'Kehilangan Momentum':**
        Jika satu rencana gagal di tengah permainan, tim kini memiliki rencana lain yang jelas. Ini dapat mencegah masalah saat transisi dari *mid* ke *late game*.
        """
    )

# ==============================================================================
# --- Halaman 5: All Data ---
# ==============================================================================

if page == "All Data":
    st.title("Bank Data")

    st.text("Semua data yang digunakan untuk analisis.")

    st.title("Team Statistics")
    st.dataframe(team_stats)

    st.title("Player NAVI Statistics")
    st.dataframe(navi_player_stats)

    st.title("Player ONIC Statistics")
    st.dataframe(onic_player_stats)

    st.title("NAVI Hero Statistics")
    st.dataframe(navi_hero_stats)

    st.title("ONIC ID Hero Statistics")
    st.dataframe(onic_hero_stats)

    st.title("All Teams Hero Statistics")
    st.text("Data from: https://id-mpl.com/statistics")
    st.dataframe(hero_stats)

    st.title("NAVI Match History")
    st.text("Data from: ")
    st.text("https://liquipedia.net/mobilelegends/Natus_Vincere/Played_Matches")
    st.text("https://www.youtube.com/@MPLIndonesia")
    st.dataframe(navi_match_history)
