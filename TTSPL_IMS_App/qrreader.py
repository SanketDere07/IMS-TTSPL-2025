import cv2

image_path = "D:/TTSPL_IMS_06_March_2025/TTSPL_IMS/media/stock_barcodes/PROD-000008_ELEC_KO_02.png"
img = cv2.imread(image_path)

if img is not None:
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if data:
        print(f"QR Code Data: {data}")
    else:
        print("No QR code detected in the image!")
else:
    print("Error: Image not found or unreadable!")
