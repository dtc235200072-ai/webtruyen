# Nhập chuỗi
s = input("Nhập chuỗi: ")

# Chuẩn hóa chuỗi
s = s.strip()              # Xóa khoảng trắng đầu và cuối
s = " ".join(s.split())    # Xóa khoảng trắng dư thừa giữa các từ
s = s.title()              # Viết hoa chữ cái đầu mỗi từ

# Thống kê
so_tu = len(s.split())
so_ky_tu = len(s.replace(" ", ""))

# In kết quả
print("Chuỗi sau khi chuẩn hóa:", s)
print("Số từ:", so_tu)
print("Số ký tự (không tính khoảng trắng):", so_ky_tu)
