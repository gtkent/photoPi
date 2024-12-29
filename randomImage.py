import random, os, sys, getopt, math
from PIL import Image, ImageDraw
from datetime import datetime

class RandomImage: 

    def __init__(self, **kwargs):
        self.numSprites = kwargs.get('numSprites', 5000)
        self.numColors = kwargs.get('numColors', 256)
        self.xDim = kwargs.get('xDim', 800)
        self.yDim = kwargs.get('yDim', 480)
        self.bgColor = kwargs.get('bgColor', "black")
        self.randFile = kwargs.get('randFile', __file__)
        self.shape = kwargs.get('shape', "random")
        self.percentFull = kwargs.get('percentFull', 100)
        self.myRandom = []
        self.image = Image.new('RGB', (self.xDim, self.yDim), self.bgColor)
        
    class MyRandom:
        
        def __init__(self, seed="NotSoRandom", numColors=256):
            self.seedRandom(seed)
            self.colors = self.genColors(numColors)

        def seedRandom(self, seed):
            random.seed(seed) 

        def randAngle(self):
            return random.randint(0,360)

        def randLineWidth(self):
            return random.randint(1,5)

        def randomColor(self):
            rgb = ( random.randint(0,255), random.randint(0,255), random.randint(0,255) )
            return rgb

        def genColors(self, numColors):
            colors = [ self.randomColor() for i in range(0, numColors) ]
            return colors

        def getColor(self):
            return self.colors[random.randint(0, len(self.colors)-1)]
    #MyRandom

    class ShapeWithRandom:

        def __init__(self, myRand, draw, shapeWidth):
            self.myRand = myRand
            self.draw = draw
            self.shapeWidth = shapeWidth

        shapeFuncs = {
            "arc" : (lambda self, coords: self.draw.arc(coords, self.myRand.randAngle(), self.myRand.randAngle(), self.myRand.getColor(), self.myRand.randLineWidth())),
            "chord" : (lambda self, coords: self.draw.chord(coords, self.myRand.randAngle(), self.myRand.randAngle(), self.myRand.getColor(), self.myRand.getColor(), self.myRand.randLineWidth())),
            "ellipse" : (lambda self, coords: self.draw.ellipse(coords, self.myRand.getColor(), self.myRand.getColor(), self.myRand.randLineWidth())),
            "line" : (lambda self, coords:self.draw.line(coords, self.myRand.getColor(), self.myRand.randLineWidth())),
            "pieSlice" : (lambda self, coords: self.draw.pieslice(coords, self.myRand.randAngle(), self.myRand.randAngle(), self.myRand.getColor(), self.myRand.getColor(), self.myRand.randLineWidth())),
            "polygon" : (lambda self, coords: self.draw.polygon(coords, self.myRand.getColor(), self.myRand.getColor())),
            "regPolygon" : (lambda self, coords: self.draw.regular_polygon((coords[0],coords[1],random.randint(1, self.shapeWidth)), random.randint(3,10), self.myRand.randAngle(), self.myRand.getColor(), self.myRand.getColor())),
            "rectangle" : (lambda self, coords: self.draw.rectangle( coords, self.myRand.getColor(), self.myRand.getColor(), self.myRand.randLineWidth())),
            "roundedRectangle" : (lambda self, coords: self.draw.rounded_rectangle( coords, random.randint(1,3), self.myRand.getColor(), self.myRand.getColor(), self.myRand.randLineWidth()))
        }
        
        def drawRandShape(self, coords):
            randShape = random.choice(list(self.shapeFuncs.keys()))
            self.shapeFuncs[randShape](self, coords)    
        
        def drawShape(self, coords, shapeFunc):
            if shapeFunc == "random":
                self.drawRandShape(coords)
            else:
                self.shapeFuncs[shapeFunc](self, coords)
    #ShapeWithRandom

    def genImage(self, shapeFunc):      
        drawing = ImageDraw.Draw(self.image)
        totalArea = self.xDim * self.yDim
        avgFillArea = self.percentFull * totalArea / 100
        avgAreaPerSprite = int(avgFillArea / self.numSprites)
        avg1DPerSprite = int(math.sqrt(avgAreaPerSprite))

        print("New Image with Area: {}, Fill Percent: {}, Fill Area: {}, Avg Sprite Area: {}, and Avg Sprite 1D: {} ".format(totalArea, self.percentFull, avgFillArea, avgAreaPerSprite, avg1DPerSprite ))    

        shape = self.ShapeWithRandom(self.myRandom, drawing, avg1DPerSprite)
        filledArea=0
        for i in range(0, self.numSprites):
            centerX = random.randint(0, self.xDim)
            centerY = random.randint(0, self.yDim)
            leftX = centerX - random.randint(0, int(avg1DPerSprite))
            leftY = centerY - random.randint(0, int(avg1DPerSprite))
            rightX = centerX + random.randint(0, int(avg1DPerSprite))
            rightY = centerY + random.randint(0, int(avg1DPerSprite)) 
            shape.drawShape( [leftX, leftY, rightX, rightY], shapeFunc )
            filledArea+= (rightX-leftX)*(rightY-leftY)

        print("Allocated Area: {}".format(filledArea/totalArea))    
 
#RandomImage    

def createRandomImage(**kwargs):
        seed = kwargs.get('randSeed', int(datetime.now().timestamp()))
        fileName = kwargs.get('fileName', datetime.now().strftime("%m.%d.%Y-%H.%M.%S")+".bmp")
        print(f"----------{fileName}")
        directory = kwargs.get('directory', 'pics/')
        print(f"----------{directory}")
        filePath = os.path.join(directory,fileName)
        
        art = RandomImage(**kwargs)
        art.myRandom = art.MyRandom(seed, art.numColors)
        art.genImage(art.shape)
        art.image.save(filePath)
        #print(f"\nCreated: {fileNamme}\n")

def main(argv):
    xDim = 800
    yDim = 480
    bgColor = "black"
    numSprites = 8000
    numColors = 256
    shape = "random"
    randFile = __file__
    helpMsg = """RandomImage.py 
                -n <numShapesPerRow> 
                -c <numColors> 
                -x <dimension> 
                -y <dimension> 
                -b <bgColor>
                -f <randSeedFile>
                -s <shape>
                    arc, chord, ellipse, line, pieSlice, polygon, regPolygon, rectangle, roundedRectangle, random (default)"""

    try:
        opts, args = getopt.getopt(argv,"hn:c:x:y:b:f:l:s:",["sprites=", "colors=", "xdim=", "ydim=", "bgColor=", "file=", "shape="])
    except getopt.GetoptError:
        print (helpMsg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print (helpMsg)
            sys.exit()
        elif opt in ("-n", "--sprites"):
            numSprites = int(arg)
        elif opt in ("-c", "--colors"):
            numColors= int(arg)
        elif opt in ("-x", "--xdim"):
            xDim = int(arg)
        elif opt in ("-y", "--ydim"):
            yDim = int(arg)           
        elif opt in ("-b", "--bgColor"):
            bgColor = arg
        elif opt in ("-f", "--file"):
            randFile = arg         
        elif opt in ("-s", "--shape"):
            shape  = arg

    art = RandomImage(numSprites, numColors, xDim, yDim, bgColor, randFile, shape)
    with open(art.randFile, "rb") as f:
        seed = f.read(250)
        art.myRandom = art.MyRandom(seed, art.numColors)
        art.genImage(art.shape)
        fileName = "pics/Image-"+datetime.now().strftime("%m.%d.%Y-%H.%M.%S")+".bmp"
        art.image.save(fileName)
        art.image.save("pics/current.bmp")
        print("\nCreated: {}\n".format(fileName))
 
if __name__ == "__main__":
    main(sys.argv[1:])