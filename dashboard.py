import streamlit as st
import pandas as pd
import plotly.express as px

# تنظیمات صفحه و پس‌زمینه
st.set_page_config(page_title="داشبورد پایش برق", layout="wide")
page_bg_img = '''
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1504384764586-bb4cdc1707b0");
    background-size: cover;
    background-attachment: fixed;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# نمایش لوگو از Base64
st.markdown(
    f"<img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAPIAAADQCAYAAAA9DDyZAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAC12SURBVHhe7Z0LvE5V+vgfctwPx12RcyRSMqhmIqIUOTIx6Ydc02Ui84t+E5VQU6' width='150'>",
    unsafe_allow_html=True
)

# ------------------ 📁 بارگذاری فایل توسط کاربر ------------------
uploaded_file = st.file_uploader("📂 لطفاً فایل اکسل کنسانتره را بارگذاری کنید", type=["xlsx"])

if uploaded_file is not None:
    sheet_name = "فرم ارائه گزارش برق کنسانتره"
    df_raw = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)

    raw_headers = df_raw.iloc[1].fillna("بدون عنوان")
    df_raw = df_raw.dropna(axis=1, how="all")
    raw_headers = raw_headers[:df_raw.shape[1]]

    def make_unique_columns(cols):
        seen = {}
        new_cols = []
        for col in cols:
            if col not in seen:
                seen[col] = 0
                new_cols.append(col)
            else:
                seen[col] += 1
                new_cols.append(f"{col}_{seen[col]}")
        return new_cols

    unique_headers = make_unique_columns(raw_headers)
    df = df_raw[2:]
    df.columns = unique_headers
    df = df.rename(columns={df.columns[0]: "تاریخ"})

    df["تاریخ"] = pd.to_datetime(df["تاریخ"], errors="coerce")
    df = df.dropna(subset=["تاریخ"])

    for col in df.columns:
        if col != "تاریخ":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ------------------ 🎛️ Sidebar ------------------
    st.sidebar.header("🎯 فیلتر بازه زمانی")
    min_date = df["تاریخ"].min()
    max_date = df["تاریخ"].max()
    start_date, end_date = st.sidebar.date_input("بازه زمانی", [min_date, max_date])
    mask = (df["تاریخ"] >= pd.to_datetime(start_date)) & (df["تاریخ"] <= pd.to_datetime(end_date))
    filtered_df = df.loc[mask]

    st.title("📊 داشبورد پایش مصرف برق تجهیزات کنسانتره")

    columns = filtered_df.select_dtypes(include="number").columns.tolist()

    # ------------------ انتخاب چند تجهیز برای مقایسه ------------------
    st.subheader("📌 مقایسه میانگین مصرف چند تجهیز")
    selected_columns = st.multiselect("🔌 انتخاب تجهیزات:", columns)

    if selected_columns:
        st.subheader("🔍 شاخص‌های کلیدی (KPI)")
        kpi_cols = st.columns(len(selected_columns))
        for i, col in enumerate(selected_columns):
            with kpi_cols[i]:
                st.metric("میانگین", f"{filtered_df[col].mean():.2f} MWh")
                st.metric("بیشترین", f"{filtered_df[col].max():.2f} MWh")
                st.metric("کمترین", f"{filtered_df[col].min():.2f} MWh")

        mean_values = filtered_df[selected_columns].mean().reset_index()
        mean_values.columns = ["تجهیز", "میانگین مصرف"]
        fig_bar = px.bar(
            mean_values,
            x="تجهیز",
            y="میانگین مصرف",
            title="📊 مقایسه میانگین مصرف برق تجهیزات",
            template="plotly_dark",
            color="تجهیز",
            text="میانگین مصرف"
        )
        fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_bar.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig_bar, use_container_width=True)

    # ------------------ نمایش نمودار خطی برای یک تجهیز خاص ------------------
    st.subheader("📈 مشاهده روند مصرف یک تجهیز")
    selected_single = st.selectbox("🧠 انتخاب تجهیز:", columns)

    if selected_single:
        fig_line = px.line(
            filtered_df,
            x="تاریخ",
            y=selected_single,
            title=f"📈 روند مصرف برق تجهیز: {selected_single}",
            template="plotly_white",
            markers=True
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # ------------------ جدول نهایی ------------------
    st.subheader("📋 جدول داده‌های فیلتر شده")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("لطفاً ابتدا فایل اکسل کنسانتره را بارگذاری کنید.")






