from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np
from scipy.interpolate import interp1d


class SelfPortrait:
    width = 400
    height = 400
    diameter = 200

    def __init__(self,
                 name,
                 skinColor=(255, 219, 172),
                 hairColor=(26, 27, 33),
                 lipColor=(220, 20, 60),
                 eyeColor=(12, 12, 45),
                 noseColor=(0, 0, 0),
                 backgroundColor=(236, 239, 241),
                 nameColor=(0,0,0)):
        self.name = name
        self.skinColor = skinColor
        self.hairColor = hairColor
        self.lipColor = lipColor
        self.eyeColor = eyeColor
        self.noseColor = noseColor
        self.backgroundColor = backgroundColor
        self.nameColor = nameColor
        self.image = Image.new("RGBA", (SelfPortrait.width,
                                        SelfPortrait.height), self.backgroundColor)
        self.canvas = ImageDraw.Draw(self.image)

    def draw(self):
        self.drawBackHair()
        self.drawFace()
        self.drawEyes()
        self.drawNose()
        self.drawMouth()
        self.drawEars()
        self.drawHair()
        self.drawName()

    def drawBackHair(self):
        center = self._centerXY()
        
        #仮にXYともに0～1の座標として描く
        #まずは右髪の輪郭
        hair_right = [
            (0,0),(0,0.1),(0,0.2),(0,0.4),(-0.05,0.8),(-0.1,1)
        ]
        #左髪の輪郭は右髪の輪郭をX=0.5で鏡像化して得る
        hair_left = self._mirrorX(hair_right,0.5)
        
        #キャンパス上の絶対座標に直すためにキャンバス上での幅・高さ・髪の毛領域の左上のXY座標を作る
        hair_width = self.diameter * 1.1
        hair_height = self.diameter * 0.5  
        hair_offset_x = center[0] - hair_width/2
        hair_offset_y = center[1]
        
        #0～1の相対座標をキャンバスの絶対座標に換算する
        hair_right = (lambda hair_coords, width, height, offset_x, offset_y: [
            (x * width + offset_x, y * height + offset_y) for x, y in hair_coords
        ])(hair_right, hair_width, hair_height, hair_offset_x, hair_offset_y)
        
        hair_left = (lambda hair_coords, width, height, offset_x, offset_y: [
            (x * width + offset_x, y * height + offset_y) for x, y in hair_coords
        ])(hair_left, hair_width, hair_height, hair_offset_x, hair_offset_y)
        
        #左髪の座標リストを反転
        hair_left.reverse()
        #右髪・左髪、それぞれ座標間をスプライン曲線で結んだものを、右と左で結合
        hair = self._makeSpline(hair_right) + self._makeSpline(hair_left)
        #ポリゴンとして描画
        self.canvas.polygon(hair, fill=self.hairColor)

    def drawFace(self):
        center = self._centerXY()
        upper_left = (center[0]-self.diameter/2, center[1]-self.diameter/2)
        lower_right = (center[0]+self.diameter/2,
                       center[1]+self.diameter/2)
        self.canvas.ellipse([upper_left, lower_right], fill=self.skinColor)

    def drawEyes(self):
        center = self._centerXY()
        eye_x_offset = self.diameter * 0.2
        eye_y_offset = self.diameter * 0.1
        r = self.diameter * 0.05
        for side in [-1, 1]:  # Left and right eyes
            x = center[0] + side * eye_x_offset
            y = center[1] + eye_y_offset
            self.canvas.ellipse(
                [(x - r, y - r), (x + r, y + r)], fill=(self.eyeColor))
            line_length = 2 * r
            angle_deg = 155 if side == -1 else 25
            angle_rad = math.radians(angle_deg)
            end_x = x + line_length * math.cos(angle_rad)
            end_y = y - line_length * math.sin(angle_rad)
            self.canvas.line([(x, y), (end_x, end_y)],
                             fill=(self.eyeColor), width=3)

    def drawNose(self):
        center = self._centerXY()
        offsetY = self.diameter * 0.2
        self.canvas.line(
            [(center[0]+5, center[1]+offsetY-10), (center[0]-5,
                                                       center[1]+offsetY), (center[0]+5, center[1]+offsetY+10)],
            fill=self.noseColor,
            width=2
        )

    def drawMouth(self):
        center = self._centerXY()
        lipCenter = (center[0], center[1]-self.diameter * 0.3)
        lipWidth = self.diameter * 0.5
        lipHeight = self.diameter * 0.7
        offsetY = self.diameter * 0.35
        self.canvas.arc(
            [(lipCenter[0]-lipWidth/2, lipCenter[1]+offsetY-lipHeight/2),
             (lipCenter[0]+lipWidth/2, lipCenter[1]+offsetY+lipHeight/2)],
            start=45,
            end=135,
            fill=self.lipColor,
            width=3
        )

    def drawEars(self):
        center = self._centerXY()
        ear_x_offset = self.diameter * 0.2
        ear_y_offset = self.diameter * 0.1
        offsetX = self.diameter * 0.47
        offsetY = self.diameter * 0.15
        r = self.diameter * 0.08
        for side in [-1, 1]:  # Left and right ears
            x = center[0] + side * offsetX
            y = center[1] + offsetY
            self.canvas.ellipse(
                [(x - r, y - r), (x + r, y + r)], fill=self.skinColor)

    def drawHair(self):
        center = self._centerXY()
        front_hair_diameter = self.diameter * 1.1
        front_hair_upper_left = (
            center[0] - front_hair_diameter / 2, center[1] - front_hair_diameter / 2)
        front_hair_lower_right = (
            center[0] + front_hair_diameter / 2, center[1] + front_hair_diameter / 2)
        self.canvas.pieslice(
            [front_hair_upper_left, front_hair_lower_right], start=180, end=360, fill=(self.hairColor))
        
    def drawName(self):
        center = self._centerXY()
        offsetY = self.diameter * 0.75
        text_size = 20
        font = ImageFont.load_default(size=text_size)         
        text_width = self.canvas.textlength(self.name,font=font)
        text_height = text_size

        # 中央揃えの座標を計算
        x = center[0] - text_width / 2
        y = center[1] + offsetY - text_height / 2

        # テキストを描画
        self.canvas.text((x, y), self.name, font=font, fill=self.nameColor)

    # ここからは内部で使う関数(継承したクラスからも使えます) ###############################
    def _centerXY(self):
        """
        キャンバス中央の座標を返す関数。

        Args:

        Returns:
            キャンバス中央の座標。[x座標,y座標]
        """
        return (SelfPortrait.width * 0.5, SelfPortrait.height*0.5)
    
    def _mirrorX(self,coordinates, mirror_x = 0):
        """
        座標のリストを指定したX座標を軸に鏡像にする関数。

        Args:
            coordinates: 座標のリスト。[(x1, y1), (x2, y2), ..., (xn, yn)] の形式。
            mirror_x: 鏡像の軸となるX座標。

        Returns:
            鏡像された座標のリスト。
        """
        mirrored_coords = []
        for x, y in coordinates:
            mirrored_x = 2 * mirror_x - x
            mirrored_coords.append((mirrored_x, y))
        return mirrored_coords
    
    def _makeSpline(self, coordinates, num_points=800):
        """
        座標のリストをスプライン曲線で滑らかに補間する関数。

        Args:
            coordinates: 座標のリスト。[(x1, y1), (x2, y2), ..., (xn, yn)] の形式。
            num_points: 補間後の点の数 = 曲線のスムーズさ

        Returns:
            補間された座標のリスト。[(x1', y1'), (x2', y2'), ..., (xn', yn')] の形式。
            x座標とy座標のリストも返す。
        """

        x_coords, y_coords = zip(*coordinates)  # x座標とy座標を分離

        # スプライン補間関数の生成 (kind='cubic'で3次スプラインを使用)
        f_x = interp1d(np.arange(len(x_coords)), x_coords, kind='cubic')
        f_y = interp1d(np.arange(len(y_coords)), y_coords, kind='cubic')

        # 新しいx座標を生成
        new_x = np.linspace(0, len(x_coords) - 1, num_points)

        # 補間されたx座標とy座標を計算
        smoothed_x = f_x(new_x)
        smoothed_y = f_y(new_x)

        # 補間された座標のリストを作成
        smoothed_coordinates = list(zip(smoothed_x, smoothed_y))

        return smoothed_coordinates
