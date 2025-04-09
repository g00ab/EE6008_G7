import cv2
import numpy as np

class ColorRecognition:
    def __init__(self):
        pass

    def rgb_to_hsv (self, r, g, b):
        # RGB color (e.g., red)
        rgb_color = np.uint8([[[r, g, b]]])  # Shape (1, 1, 3)

        # Convert to HSV
        hsv_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)
        print(hsv_color)
        return hsv_color

    def image_manipulation(self, image_path, target_h, target_s, target_v, h_tol, s_tol, v_tol):
        # Read the image
        self.image_bgr = cv2.imread(image_path)

        # Convert to HSV color space
        image_hsv = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2HSV)

        # Create the lower and upper bounds for the mask
        lower_bound = np.array([target_h - h_tol, target_s - s_tol, target_v - v_tol])
        upper_bound = np.array([target_h + h_tol, target_s + s_tol, target_v + v_tol])

        # Create the mask
        self.mask = cv2.inRange(image_hsv, lower_bound, upper_bound)

        # Apply the mask to the original image
        self.result = cv2.bitwise_and(self.image_bgr, self.image_bgr, mask=self.mask)

        return self.result


    def showing_results(self):
        # Optional: show results
        cv2.imshow('Original Image', self.image_bgr)
        cv2.imshow('Filtered Yellow Mask', self.mask)
        cv2.imshow('Filtered Result', self.result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



def main ():

    colorRecognition = ColorRecognition()

    image_bgr = cv2.imread('./screenshots_cube/green.class/00000.jpg') 
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # Example RGB values
    yellow ={
        'r': 146, 
        'g': 138,
        'b':  37
}
    red = {
        'r': 98,
        'g': 8,
        'b': 8
    }
    orange = {
        'r': 175,
        'g': 75,
        'b': 26
    }
    white = {
        'r': 171,
        'g': 178,
        'b': 170
    }
    blue = {
        'r': 9,
        'g': 39,
        'b': 77
    }
    green = {
        'r': 20,
        'g': 90,
        'b': 2
    }

    

    # Convert to HSV
    yellow_hsv = colorRecognition.rgb_to_hsv(yellow['r'], yellow['g'], yellow['b'])[0][0]
    red_hsv =colorRecognition.rgb_to_hsv(red['r'], red['g'], red['b'])[0][0]
    green_hsv =colorRecognition.rgb_to_hsv(green['r'], green['g'], green['b'])[0][0]
    white_hsv =colorRecognition.rgb_to_hsv(white['r'], white['g'], white['b'])[0][0]
    orange_hsv =colorRecognition.rgb_to_hsv(orange['r'], orange['g'], orange['b'])[0][0]
    blue_hsv =colorRecognition.rgb_to_hsv(blue['r'], blue['g'], blue['b'])[0][0]

    
    colorRecognition.image_manipulation('./screenshots_cube/green.class/00008.jpg', green_hsv[0], green_hsv[1], green_hsv[2], 50, 60, 70)
    colorRecognition.showing_results()
    colorRecognition.image_manipulation('./screenshots_cube/white.class/00009.jpg', white_hsv[0], white_hsv[1], white_hsv[2], 85, 50, 50)
    colorRecognition.showing_results()
    colorRecognition.image_manipulation('./screenshots_cube/yellow.class/00008.jpg', yellow_hsv[0], yellow_hsv[1], yellow_hsv[2], 10, 85, 70)
    colorRecognition.showing_results()
    colorRecognition.image_manipulation('./screenshots_cube/orange.class/00008.jpg', orange_hsv[0], orange_hsv[1], orange_hsv[2], 10, 50, 50)
    colorRecognition.showing_results()
    colorRecognition.image_manipulation('./screenshots_cube/red.class/00008.jpg', red_hsv[0], red_hsv[1], red_hsv[2], 25, 70, 70)
    colorRecognition.showing_results()
    colorRecognition.image_manipulation('./screenshots_cube/blue.class/00011.jpg', blue_hsv[0], blue_hsv[1], blue_hsv[2], 10, 35, 35)
    colorRecognition.showing_results()


if __name__ == "__main__":
    main()