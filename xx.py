import os
import argparse
import re
from alphabets import plate_chr

#    python3 trains/crnn_plate_recognition/xx.py --image_path dataset/htc_plates/train --label_file trains/crnn_plate_recognition/datasets/train.txt
#    python3 trains/crnn_plate_recognition/xx.py --image_path dataset/htc_plates/val --label_file trains/crnn_plate_recognition/datasets/val.txt

def allFileList(rootfile, allFile):
    """递归获取所有文件"""
    for temp in os.listdir(rootfile):
        fileName = os.path.join(rootfile, temp)
        if os.path.isfile(fileName):
            allFile.append(fileName)
        else:
            allFileList(fileName, allFile)

def is_str_right(plate_name, plateDict):
    """检查车牌名是否都在 plateDict 中"""
    for ch in plate_name:
        if ch not in plateDict:
            return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_path', type=str, default="/mnt/EPan/carPlate/@realTest2_noTraining/realrealTest", help='图片根目录') 
    parser.add_argument('--label_file', type=str, default='datasets/val.txt', help='输出标签文件')  
    opt = parser.parse_args()

    rootPath = opt.image_path
    labelFile = opt.label_file
    plateDict = {ch: i for i, ch in enumerate(plate_chr)}

    file_list = []
    allFileList(rootPath, file_list)

    mainland_count = 0
    hk_count = 0
    taiwan_count = 0
    illegal_files = []
    picNum = 0

    with open(labelFile, "w", encoding="utf-8") as fp:
        for jpgFile in file_list:
            jpgName = os.path.basename(jpgFile)

            # 忽略隐藏文件
            if jpgName.startswith('.'):
                illegal_files.append(jpgFile)
                continue

            # 检查整个文件名是否有非法字符
            if re.search(r'[^0-9A-Za-z\u4e00-\u9fff_\.]', jpgName):
                illegal_files.append(jpgFile)
                continue

            name = jpgName.split("_")[0].upper()  # 车牌名，大写统一

            if not is_str_right(name, plateDict):
                illegal_files.append(jpgFile)
                continue

            # 分类统计
            first_char = name[0]
            if '\u4e00' <= first_char <= '\u9fff':
                mainland_count += 1
            elif first_char in ['H', 'K', 'M', 'O']:  # 港澳/特别标识
                hk_count += 1
            else:  # 台湾或其他
                taiwan_count += 1

            # 写入标签
            labelStr = " " + " ".join(str(plateDict[ch]) for ch in name)
            fp.write(os.path.abspath(jpgFile) + labelStr + "\n")
            picNum += 1

    print(f"✅ 标签文件生成完毕: {labelFile}")
    print(f"   总有效图片数: {picNum}")
    print(f"   大陆车: {mainland_count}")
    print(f"   港澳车: {hk_count}")
    print(f"   台湾车/其他: {taiwan_count}")
    print(f"⚠️ 被排除的非法文件数: {len(illegal_files)}")
    if illegal_files:
        print("   以下文件名含非法字符或无法解析:")
        for f in illegal_files:
            print(f"   {f}")
