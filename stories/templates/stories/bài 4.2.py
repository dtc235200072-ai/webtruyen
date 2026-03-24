import os
thu_muc = "duong_dan_thu_muc"
tu_khoa = "file_name"
files = os.listdir(thu_muc)
for i, file in enumerate(files, start=1):
    duoi_file = os.path.splitext(file)[1]
    ten_moi = f"{tu_khoa}_{i}{duoi_file}"
    os.rename(
        os.path.join(thu_muc, file),
        os.path.join(thu_muc, ten_moi)
    )
