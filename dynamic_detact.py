import cv2

# create Background Subtractor objects
bs = cv2.createBackgroundSubtractorKNN(detectShadows=True)

history = 10
bs.setHistory(history)

_es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

counter = 0


def dynamic_area_detect(frame, ignore_area=[], min_size=500, max_size=22000):
    """ignore_area： 忽略检测区域[[x, y, w, h]"""
    global bs, counter
    fgmask = bs.apply(frame)
    if counter < history:
        print(counter, end='\t')
        counter += 1
        return []

    fg2 = fgmask.copy()
    # 二值化阈值处理
    th = cv2.threshold(fg2, 244, 255, cv2.THRESH_BINARY)[1]
    for i in ignore_area:
        x, y, w, h = i
        th[y: y+h, x:x+w] = 0
# 形态学膨胀
## 1
    th = cv2.erode(th, _es, iterations=2)
    dilated = cv2.dilate(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 3)), iterations=2)
## 2
    # dilated = cv2.dilate(th, _es, iterations=2)
##
    contours, hier = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    target_area = []
    for c in contours:
        if min_size < cv2.contourArea(c) < max_size:
            # 该函数计算矩形的边界框
            (x, y, w, h) = cv2.boundingRect(c)
            target_area.append((x, y, w, h))
            cv2.rectangle(dilated, (x, y), (x + w, y + h), (255, 255, 0), 3)

    cv2.imwrite('test\\' + str(counter) + '.jpg', dilated)
    # cv2.imshow("mog", fgmask)
    # cv2.imshow("thresh", th)
    cv2.imshow('dilated', dilated)

    print('Frame %d Dynamic Arae Number: %d' % (counter, len(target_area)))
    print(target_area)
    counter += 1
    return target_area


if __name__ == '__main__':

    camera = cv2.VideoCapture('data\\video\\chaplin.mp4')
    # camera = cv2.VideoCapture(0)  # 参数0表示第一个摄像头
    # 判断视频是否打开
    if camera.isOpened():
        print('Open')
    else:
        print('摄像头未打开')

    # 测试用,查看视频size
    # size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
    #         int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    # print('size:' + repr(size))

    while True:
        ret, frame = camera.read()
        areas = dynamic_area_detect(frame)

        for c in areas:
            (x, y, w, h) = c
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        cv2.imshow("detection", frame)
        if cv2.waitKey(1) & 0xff == 27:
            break
    camera.release()
    cv2.destroyAllWindows()
