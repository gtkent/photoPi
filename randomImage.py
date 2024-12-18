import argparse, random, sys, getopt, math
from PIL import Image, ImageDraw, ImageOps
from datetime import datetime, time

class RandomImage: 

    def __init__(self, numSprites=5000, numColors=256, xDim=800, yDim=480, randFile=__file__, shape="random", percentFull=100):
        self.numSprites = numSprites
        self.numColors = numColors
        self.xDim = xDim
        self.yDim = yDim
        self.randFile = randFile
        self.shape = shape
        self.percentFull = percentFull
        self.myRandom = []
        self.compImage = []
        self.images = []
        
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
        baseImg = Image.new('RGB', (self.xDim, self.yDim), color=(255,255,255))
        drawing = ImageDraw.Draw(baseImg)
       
        """ 
        maxShapeWidth = int(self.xDim/self.numSprites)
        maxShapeHeight = int(self.yDim/self.numSprites)
        shape = self.ShapeWithRandom(self.myRandom, drawing, maxShapeWidth)        
        for x in range(0, self.numSprites+10):
            for y in range(0, self.numSprites+10):
                leftX = x*maxShapeWidth + random.randint(0, maxShapeWidth)
                leftY = y*maxShapeHeight + random.randint(0, maxShapeHeight)
                rightX = leftX + maxShapeWidth - random.randint(1, maxShapeWidth)
                rightY = leftY + maxShapeHeight - random.randint(1, maxShapeHeight)
                shape.drawShape( [leftX, leftY, rightX, rightY], shapeFunc )
        """

        totalArea = self.xDim * self.yDim
        avgFillArea = self.percentFull * totalArea / 100
        avgAreaPerSprite = int(avgFillArea / self.numSprites)
        avg1DPerSprite = int(math.sqrt(avgAreaPerSprite))

        print("New Images with Area: {}, Fill Percent: {}, Fill Area: {}, Avg Sprite Area: {}, and Avg Sprite 1D: {} ".format(totalArea, self.percentFull, avgFillArea, avgAreaPerSprite, avg1DPerSprite ))    

        shape = self.ShapeWithRandom(self.myRandom, drawing, avg1DPerSprite)
        filledArea=0
        for i in range(0, self.numSprites):
            centerX = random.randint(0, self.xDim)
            centerY = random.randint(0, self.yDim)
            leftX = centerX - random.randint(0, int(avg1DPerSprite))
            leftY = centerY - random.randint(0, int(avg1DPerSprite))
            rightX = centerX + random.randint(0, int(avg1DPerSprite))
            rightY = centerY + random.randint(0, int(avg1DPerSprite)) 
            """
            leftX = centerX - int(avg1DPerSprite)
            leftY = centerY - int(avg1DPerSprite)
            rightX = centerX + int(avg1DPerSprite)
            rightY = centerY + int(avg1DPerSprite)
            """ 
            shape.drawShape( [leftX, leftY, rightX, rightY], shapeFunc )
            filledArea+= (rightX-leftX)*(rightY-leftY)

        print("Allocated Area: {}".format(filledArea/totalArea))    
        return baseImg

    def createImages(self, shape):
        with open(self.randFile, "rb") as f:
            while (seedBytes := f.read(250)):
                self.myRandom.seedRandom(seedBytes)
                self.images.append(self.genImage(shape))

    def blend(self):
        for i in range(1, len(self.images)):
            self.images[i] = Image.blend(self.images[i-1], self.images[i], 0.5)
        
        self.images[0] = Image.blend(self.images[0], self.images[-1], 0.5)

    def blend2(self, blendFile):
        with Image.open(blendFile) as im:
            im = im.resize((self.xDim,self.yDim)).convert("L")
            im = ImageOps.invert(im)
            self.compImage = im.convert("RGBA")
            for i in range(0, len(self.images)):
                self.images[i] = Image.blend(self.images[i], self.compImage, 0.5)

    def composite(self, compFile):
        with Image.open(compFile) as im:
            im = im.resize((self.xDim,self.yDim)).convert("L")
            im = ImageOps.invert(im)
            self.compImage = im.convert("RGBA")
            for i in range(0, len(self.images)):
                self.images[i] = Image.alpha_composite(self.compImage, self.images[i])

#RandomImage    

def main(argv):
    xDim = 800
    yDim = 480
    numSprites = 8000
    numColors = 256
    shape = "random"
    randFile = __file__
    helpMsg = """RandomImage.py 
                -n <numShapesPerRow> 
                -c <numColors> 
                -x <dimension> 
                -y <dimension> 
                -f <randSeedFile>
                -s <shape>
                    arc, chord, ellipse, line, pieSlice, polygon, regPolygon, rectangle, roundedRectangle, random (default)"""

    try:
        opts, args = getopt.getopt(argv,"hn:c:x:y:f:l:s:",["sprites=", "colors=", "xdim=", "ydim=", "file=", "shape="])
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
        elif opt in ("-f", "--file"):
            randFile = arg         
        elif opt in ("-s", "--shape"):
            shape  = arg

    art = RandomImage(numSprites, numColors, xDim, yDim, randFile, shape)
    with open(art.randFile, "rb") as f:
        seed = f.read(250)
        art.myRandom = art.MyRandom(seed, art.numColors)
        art.images.append(art.genImage(art.shape))
        fileName = "pics/Image-"+datetime.now().strftime("%m.%d.%Y-%H.%M.%S")+".gif"
        art.images[0].save(fileName)
        print("\nCreated: {}\n".format(fileName))
 
if __name__ == "__main__":
    main(sys.argv[1:])