import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# -------------------------
# Cấu hình trang Streamlit
# -------------------------
st.set_page_config(page_title="Đăng ký phúc khảo", layout="wide")

# -------------------------
# Phân quyền truy cập
# -------------------------
st.sidebar.title("🔑 Đăng nhập")
role = st.sidebar.radio("Bạn là:", ["Sinh viên", "Cán bộ quản lý"])

is_admin = False
if role == "Cán bộ quản lý":
    password = st.sidebar.text_input("🔐 Nhập mật khẩu:", type="password")
    if password:
        if password == "admin123":
            is_admin = True
        else:
            st.sidebar.warning("❌ Mật khẩu sai! Vui lòng nhập lại.")

# -------------------------
# Đường dẫn file lưu trữ
# -------------------------
TIME_FILE = "thoi_gian_dang_ky.txt"
KHOA_FILE = "danh_sach_khoa_hoc.xlsx"
REGISTRATION_FILE = "danh_sach_dang_ky.xlsx"

# -------------------------
# CHỨC NĂNG CHO CÁN BỘ QUẢN LÝ (Admin)
# -------------------------
if is_admin:
    st.sidebar.subheader("📅 Thiết lập thời gian đăng ký")
    admin_start_date = st.sidebar.date_input("📆 Ngày bắt đầu", value=date.today(), key="admin_start")
    admin_end_date = st.sidebar.date_input("⏳ Ngày kết thúc", value=date.today(), key="admin_end")
    if st.sidebar.button("💾 Lưu thời gian đăng ký"):
        try:
            with open(TIME_FILE, "w") as f:
                # Lưu theo định dạng YYYY-MM-DD
                f.write(f"{admin_start_date}\n{admin_end_date}")
            st.sidebar.success("✅ Đã lưu thời gian đăng ký!")
        except Exception as e:
            st.sidebar.error(f"❌ Lỗi khi lưu thời gian: {e}")

    # Tải file danh sách Khoa & Học phần
    uploaded_file = st.sidebar.file_uploader("📥 Tải danh sách Khoa & Học phần (Excel)", type=["xlsx"])
    if uploaded_file:
        try:
            df_khoa = pd.read_excel(uploaded_file, sheet_name="Khoa")
            df_hoc_phan = pd.read_excel(uploaded_file, sheet_name="HocPhan")
            with pd.ExcelWriter(KHOA_FILE) as writer:
                df_khoa.to_excel(writer, sheet_name="Khoa", index=False)
                df_hoc_phan.to_excel(writer, sheet_name="HocPhan", index=False)
            st.sidebar.success("✅ Đã tải danh sách Khoa & Học phần thành công!")
        except Exception as e:
            st.sidebar.error(f"❌ Lỗi khi tải file: {e}")

    # Cho phép tải danh sách đăng ký dưới dạng file Excel
    st.sidebar.subheader("Tải danh sách đăng ký")
    if os.path.exists(REGISTRATION_FILE):
        with open(REGISTRATION_FILE, "rb") as f:
            reg_data = f.read()
        st.sidebar.download_button(
            label="📥 Tải file danh sách đăng ký",
            data=reg_data,
            file_name="danh_sach_dang_ky.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.sidebar.info("Chưa có đăng ký nào.")

# -------------------------
# ĐỌC THỜI GIAN ĐĂNG KÝ (cho cả 2 vai trò)
# -------------------------
if os.path.exists(TIME_FILE):
    try:
        with open(TIME_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                start_date = datetime.strptime(lines[0].strip(), "%Y-%m-%d").date()
                end_date = datetime.strptime(lines[1].strip(), "%Y-%m-%d").date()
            else:
                start_date, end_date = None, None
    except Exception as e:
        st.error(f"Lỗi đọc file thời gian đăng ký: {e}")
        start_date, end_date = None, None
else:
    start_date, end_date = None, None

# -------------------------
# ĐỌC DANH SÁCH KHOA & HỌC PHẦN
# -------------------------
if os.path.exists(KHOA_FILE):
    try:
        df_khoa = pd.read_excel(KHOA_FILE, sheet_name="Khoa")
        df_hoc_phan = pd.read_excel(KHOA_FILE, sheet_name="HocPhan")
    except Exception as e:
        st.error(f"❌ Lỗi khi đọc file {KHOA_FILE}: {e}")
        df_khoa = pd.DataFrame(columns=["Khoa"])
        df_hoc_phan = pd.DataFrame(columns=["Khoa", "Tên học phần"])
else:
    df_khoa = pd.DataFrame(columns=["Khoa"])
    df_hoc_phan = pd.DataFrame(columns=["Khoa", "Tên học phần"])

# Tạo dictionary ánh xạ giữa Khoa và danh sách Học phần tương ứng
khoa_hoc_phan = {k: list(df_hoc_phan[df_hoc_phan["Khoa"] == k]["Tên học phần"]) for k in df_khoa.get("Khoa", [])}

# -------------------------
# GIAO DIỆN SINH VIÊN - ĐĂNG KÝ PHÚC KHÁO
# -------------------------
if role == "Sinh viên":
    # Kiểm tra thời gian đăng ký
    if start_date and end_date:
        st.info(f"📅 **Thời gian đăng ký phúc khảo:** {start_date} ➝ {end_date}")
        today = date.today()
        if today < start_date:
            st.warning("⏳ Đăng ký chưa bắt đầu! Vui lòng quay lại sau.")
            st.stop()
        elif today > end_date:
            st.error("❌ Thời gian đăng ký đã kết thúc! Bạn không thể đăng ký nữa.")
            st.stop()
    else:
        st.error("❌ Thời gian đăng ký chưa được thiết lập. Vui lòng liên hệ Cán bộ quản lý.")
        st.stop()

    st.header("📌 Biểu mẫu đăng ký phúc khảo")
    # --- Phần nhập thông tin cá nhân và lựa chọn môn (bên ngoài form) ---
    email = st.text_input("📧 Email sinh viên:")
    ho_ten = st.text_input("📌 Họ tên:")
    mssv = st.text_input("🎓 Mã số sinh viên:")
    if khoa_hoc_phan:
        khoa = st.selectbox("🏫 Chọn Khoa:", list(khoa_hoc_phan.keys()))
    else:
        khoa = ""
    he_dao_tao = st.selectbox("📖 Hệ đào tạo:", ["Hệ Chuẩn", "Hệ CLC", "Hệ Chuẩn Quốc tế"])
    # Widget chọn môn được đặt bên ngoài form để thay đổi sẽ render ngay lập tức
    selected_courses = st.multiselect("📚 Chọn môn phúc khảo:", options=khoa_hoc_phan.get(khoa, []))
    
    # --- Phần nhập chi tiết cho từng môn (được nhóm trong form) ---
    with st.form(key="detailed_form"):
        course_data = []
        if selected_courses:
            st.markdown("### Thông tin chi tiết cho từng môn")
            # Hiển thị header cho bảng nhập chi tiết
            col0, col1, col2, col3, col4 = st.columns(5)
            col0.write("Môn")
            col1.write("Phòng thi")
            col2.write("Ca thi")
            col3.write("Ngày thi")
            col4.write("Điểm công bố")
            # Với mỗi môn được chọn, hiển thị một dòng nhập liệu
            for mon in selected_courses:
                c0, c1, c2, c3, c4 = st.columns(5)
                c0.write(mon)
                phong_thi = c1.text_input("", key=f"phong_thi_{mon}")
                ca_thi = c2.selectbox("", ["Ca 1", "Ca 2", "Ca 3", "Ca 4"], key=f"ca_thi_{mon}")
                ngay_thi = c3.date_input("", key=f"ngay_thi_{mon}")
                diem_cong_bo = c4.number_input("", min_value=0.0, max_value=10.0, step=0.1, key=f"diem_cong_bo_{mon}")
                course_data.append({
                    "Email": email,
                    "Họ tên": ho_ten,
                    "MSSV": mssv,
                    "Khoa": khoa,
                    "Hệ đào tạo": he_dao_tao,
                    "Tên học phần": mon,
                    "Phòng thi": phong_thi,
                    "Ca thi": ca_thi,
                    "Ngày thi": ngay_thi,
                    "Điểm công bố": diem_cong_bo
                })
        submit = st.form_submit_button("📩 Gửi Đăng Ký")

        if submit:
            # Kiểm tra định dạng email
            if not email.lower().endswith("@hcmussh.edu.vn"):
                st.error("Email không hợp lệ. Email phải có đuôi @hcmussh.edu.vn")
            # Kiểm tra các thông tin cá nhân đã được điền đầy đủ
            elif not email or not ho_ten or not mssv or not khoa or not he_dao_tao:
                st.error("Vui lòng điền đầy đủ thông tin cá nhân.")
            elif not selected_courses:
                st.error("Vui lòng chọn ít nhất một môn phúc khảo.")
            else:
                # Kiểm tra các trường chi tiết của từng môn phải được điền đầy đủ
                incomplete = False
                for data in course_data:
                    if data["Phòng thi"] == "" or data["Ca thi"] == "" or data["Ngày thi"] is None or data["Điểm công bố"] is None:
                        incomplete = True
                        break
                if incomplete:
                    st.error("Vui lòng điền đầy đủ thông tin cho tất cả các môn phúc khảo.")
                else:
                    try:
                        # Lưu đăng ký vào file Excel
                        if os.path.exists(REGISTRATION_FILE):
                            df_reg = pd.read_excel(REGISTRATION_FILE)
                        else:
                            df_reg = pd.DataFrame(columns=["Email", "Họ tên", "MSSV", "Khoa", "Hệ đào tạo",
                                                           "Tên học phần", "Phòng thi", "Ca thi", "Ngày thi", "Điểm công bố"])
                        df_new = pd.DataFrame(course_data)
                        df_reg = pd.concat([df_reg, df_new], ignore_index=True)
                        df_reg.to_excel(REGISTRATION_FILE, index=False)
                        st.success("✅ Đăng ký thành công!")
                        st.balloons()
                        # Hiển thị bảng đăng ký của sinh viên (lấy theo email)
                        df_reg_all = pd.read_excel(REGISTRATION_FILE)
                        df_reg_self = df_reg_all[df_reg_all["Email"].str.lower() == email.lower()]
                        st.markdown("### Thông tin đăng ký của bạn:")
                        st.dataframe(df_reg_self)
                    except Exception as e:
                        st.error(f"❌ Lỗi khi lưu đăng ký: {e}")