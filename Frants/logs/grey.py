import cv2,os
import numpy as np

# Load the image
image = cv2.imread(os.path.join(os.path.dirname(__file__),"archive","NEU-DET","train","images","inclusion","inclusion_80.jpg"))

# Convert to grayscale
# gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply simple binary thresholding
# Arguments: source image, threshold value, max value, threshold type
# Pixels with intensity > 127 become 255 (white), others become 0 (black)
thresholde = 65
ret, thresholded_image1 = cv2.threshold(image, thresholde, 255, cv2.THRESH_BINARY)
# res = cv2.adaptiveThreshold(gray_img,255,cv2.ADAPTIVE_THRESH_MEAN_C,
#             cv2.THRESH_BINARY,11,2)
denoised_image = cv2.medianBlur(thresholded_image1, 3) # (5,5) is kernel size, 0 is sigmaX

ret, thresholded_image = cv2.threshold(denoised_image, 127, 255, cv2.THRESH_BINARY)
# kernel_size = 5

# kernel = np.ones((kernel_size, kernel_size), np.uint8)

# mask_opened = cv2.morphologyEx(thresholded_image, cv2.MORPH_OPEN, kernel)

# # 1. Создаем маску черных дефектов
# lower_black = np.array([0, 0, 0])
# upper_black = np.array([20, 20, 20]) # Чувствительность к черному
# mask = cv2.inRange(mask_opened, lower_black, upper_black)

# # 2. Применяем inpainting
# # inpaintRadius=3 — радиус области вокруг, которую анализировать
# # cv2.INPAINT_TELEA — алгоритм восстановления
# result = cv2.inpaint(mask_opened, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

# Display the original and thresholded images (optional)
cv2.imshow('Original Image', image)
# cv2.imshow('Gray Image', gray_img)
# cv2.imshow('Adaptive Image', res)
cv2.imshow('Thresh 1 Image', thresholded_image1)
cv2.imshow('Thresh 2 Image', thresholded_image)
cv2.imshow('Noiseless Image', denoised_image)
# cv2.imshow('Grayscale Image', image)
# cv2.imshow('Thresholded Image', thresholded_image)
cv2.waitKey(0)
cv2.destroyAllWindows()


