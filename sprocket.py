#!/usr/bin/python

# Sprocket.py: A configuration generator for the Custom Ore Generation:
#              First Revival add-on for Minecraft.  The program reads
#              the mod's name and list of ores from a simple file, and
#              then generates the xml configuration file that can be
#              inserted into COG for play.  Keep in mind that the
#              generated file is *basic*, this was designed to make
#              clean files for further refinement without all the
#              tedious searching for missing brackets or broken 
#              elements.

# UPDATE - 4/11/2015 - Script completely rewritten for more options and
#              flexibility.  

import random
import ConfigParser
import json
import sys
import textwrap
import string

def randomHexNumber(length):
    return ''.join([random.choice('0123456789ABCDEF') for x in range(length)])

def indentText(level):
    spaceHolder = ""
    for i in range (0, level):
        spaceHolder += "    "
        
    return spaceHolder

# Initialize variables

configFile = sys.argv[1]
modName = ""        # This is the mod name component for variable names
modPrefix = ""      # This comes before the ore name in variable names
                    #     (tic, mtlg)

# Initialize Ore Options
oreName = []          # The name of this specific Ore
oreConfigName = []    # Ore name without the spaces
oreWorld = []         # The world the ore spawns in
                      #    (Overworld, Nether, End)
oreBlock = []         # The ore's actual block id
oreMeta = []          # The meta number, if not 0
oreReplace = []       # The block the ore replaces
orePipe = []          # Content of pipe distribution (usually lava)
oreDistributions = [] # Comma-separated list of distribution options.
oreWireframe = []     # Wireframe color (0x60 followed by web code)
oreHeight = []        # Center level for ore distributions
oreRange = []         # Level range between lowest and highest point
oreFrequency = []     # Ore Frequency Multiplier
oreSize = []          # Ore Size Multiplier
oreBiomes = []        # Ores only spawn in these biomes
orePreferBiomes = []  # Ores spawn extra in these biomes
oreScale = []         # COG Surface Scaling

oreList = ""
indentLine=0

# Open a configuration file for reading, and prepare defaults.
Config = ConfigParser.SafeConfigParser(
    defaults={'Block':'MISSING',
              'World':'Overworld',
              'Meta':'0',
              'Replace':'minecraft:stone',
              'Pipe':'minecraft:lava',
              'Distribution':'Vanilla',
              'Wireframe':'0x60'+randomHexNumber(6),
              'Height':'64',
              'Range':'64',
              'Frequency':'1',
              'Size':'1',
              'Biomes':'ALL',
              'Prefers':'NONE',
              'Scale':'Biome'
    })
Config.read(configFile)

# Get the mod's name in three forms, one for mod-specific variables,
# one for display in strings, and a prefix to use for ore variables.
modName = Config.get('Mod', 'Name')  # "My Mod 2"
modPrefix = Config.get('Mod', 'Prefix') # "mmd2"
modDetect = Config.get('Mod', 'Detect') # "MyMod"

                    
modConfigName=modName.replace(" ", "")

oreName = Config.sections()
oreName.pop(0) # The first section is not an ore, it's the mod's
               # settings.  It needs to go.

oreCount = 0
errorCondition = ""

# Creating a set of lists for the options; memory access is always
# faster than disk access.


for currentOre in oreName:
    oreConfigName.append(oreName[oreCount].replace(" ", ""))
    oreBlock.append(Config.get(currentOre, 'Block'))
    oreWorld.append(Config.get(currentOre, 'World'))
    oreMeta.append(Config.get(currentOre, 'Meta'))
    oreReplace.append(Config.get(currentOre, 'Replace'))
    orePipe.append(Config.get(currentOre, 'Pipe'))
    oreDistributions.append(Config.get(currentOre, 'Distributions'))
    oreWireframe.append(Config.get(currentOre, 'Wireframe'))
    oreHeight.append(Config.get(currentOre, 'Height'))
    oreRange.append(Config.get(currentOre, 'Range'))
    oreFrequency.append(Config.get(currentOre, 'Frequency'))
    oreSize.append(Config.get(currentOre, 'Size'))
    oreBiomes.append(Config.get(currentOre, 'Biomes'))
    orePreferBiomes.append(Config.get(currentOre, 'Prefers'))
    oreScale.append(Config.get(currentOre, 'Scale'))    
    
    # Check to make sure the Block value is valid.
    if Config.get(currentOre, 'Block') == 'MISSING':
        print('Warning: The \'['+currentOre+']\' section is missing a block name.')
        errorCondition = 'T'
    
    oreCount += 1

# All ore data has been imported from the configuration file.  Now we 
# need to generate the actual XML configuration.

# First, we'll set up the variables that will hold the generated text
# until everything is ready to be written to the new file.
headerTemplate = ""
controlsTemplate = []
oreConfigTemplate = []

########################## MAKE CONFIG HEADING #######################

def headerGen():
    oreList = ", ".join(oreName)
    fmtOreList = "\r\n".join(textwrap.wrap(oreList, 70))
    return "\n\
<!-- ================================================================ \n\
\n\
Custom Ore Generation:   "+modName+" Module\n\n\
Generates: "+fmtOreList+"\n\
\n\
================================================================ -->\n\n"

##################### BIOME LISTING ###########################
# This limits ore generation to specific biomes, based on the
# Forge Biome Dictionary.

def biomeSet(biome):
    global indentLine
    biomeCommand = indentText(indentLine)+"<BiomeType name='"+biome+"'/>\n"
    
    return biomeCommand
    

def biomeList(currentBiomeList):
    biomeList = currentBiomeList.split(',')
    biomeCommandList = ""
    
    for biomeSelect in range (0, len(biomeList)):
        biomeCommandList += biomeSet(biomeList[biomeSelect])
        if biomeList[biomeSelect] == "ALL":
            biomeCommandList = ""
    
    return biomeCommandList

################## CHOOSE DISTRIBUTION OPTIONS #####################

def distributionControlGen(currentOreDistBase):
    global indentLine
    currentOreDist = currentOreDistBase.replace(" ", "")
    if currentOreDist == 'Vanilla': # uses StandardGen
        optionText = indentText(indentLine)+"<Choice value='vanillaStdGen' displayValue='Vanilla'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Vanilla-style clusters.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText
        
    elif currentOreDist == 'LayeredVeins': # uses Veins
        optionText = indentText(indentLine)+"<Choice value='layeredVeins' displayValue='Layered Veins'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Layered Veins.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText
               
    elif currentOreDist == 'VerticalVeins': # uses Veins
        optionText = indentText(indentLine)+"<Choice value='verticalVeins' displayValue='Vertical Veins'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Vertical Veins.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText
               
    elif currentOreDist == 'SmallDeposits': # uses Veins
        optionText = indentText(indentLine)+"<Choice value='smallDeposits' displayValue='Small Deposits'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Small Deposits.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText
        
    elif currentOreDist == 'Geodes': # uses Veins
        optionText = indentText(indentLine)+"<Choice value='geodes' displayValue='Geodes'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Geodes.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText
        
    elif currentOreDist == 'HugeVeins': # uses Veins
        optionText = indentText(indentLine)+"<Choice value='hugeVeins' displayValue='Huge Veins'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Huge Veins.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText
        
    elif currentOreDist == 'SparseVeins': # uses Veins
        optionText = indentText(indentLine)+"<Choice value='sparseVeins' displayValue='Sparse Veins'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Sparse Veins.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText

    elif currentOreDist == 'PipeVeins': # uses Veins
        optionText = indentText(indentLine)+"<Choice value='pipeVeins' displayValue='Pipe Veins'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Pipe Veins.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText

    elif currentOreDist == 'CompoundVeins': # uses Veins
        optionText = indentText(indentLine)+"<Choice value='compoundVeins' displayValue='Compound Veins'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Compound Veins.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText
        
    elif currentOreDist == 'StrategicCloud': # uses Cloud
        optionText = indentText(indentLine)+"<Choice value='strategicCloud' displayValue='Clouds'>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        optionText += indentText(indentLine)+"Strategic Clouds.\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Description>\n"
        indentLine -= 1
        optionText += indentText(indentLine)+"</Choice>\n"
        return optionText
        
    else:
        print "There is no '"+currentOreDist+"' distribution!"
        errorCondition = 'T'

################### CONFIGURATION SETUP ##############################
# Assembles the configuration section for in-game setup.

def controlsGen(currentOreGen):
    global indentLine
    
    oreConfigName=modPrefix+oreName[currentOreGen]
    oreConfigName=oreConfigName.replace(" ", "")
    
    # Opening
    configScriptOpen = indentText(indentLine)+"<!-- "+oreName[currentOreGen]+" Configuration UI -->\n"
    configScriptOpen += indentText(indentLine)+"<OptionChoice name='"+oreConfigName+"Dist' displayState='shown' displayGroup='group"+modConfigName+"'> \n"
    indentLine += 1
    configScriptOpen += indentText(indentLine)+"<Description> Controls how "+oreName[currentOreGen]+" is generated </Description> \n"
    configScriptOpen += indentText(indentLine)+"<DisplayName>"+modName+" "+oreName[currentOreGen]+" Type</DisplayName>\n"
    
    # Actual Configuration List
    # Start with an empty script
    configScriptList = ""
    
    # The list of ore distributions will determine available options.
    distributionList = oreDistributions[currentOreGen]
    distributionList = distributionList.split(',')
    for distribution in distributionList:
         configScriptList += distributionControlGen(distribution)
    
    # Closing
    configScriptClose = indentText(indentLine)+"<Choice value='none' displayValue='None' description='"+oreName[currentOreGen]+" is not generated in the world.'/>\n"
    indentLine -= 1
    configScriptClose += indentText(indentLine)+"</OptionChoice>\n"
    configScriptClose += indentText(indentLine)+"<OptionNumeric name='"+oreConfigName+"Freq' default='1'  min='0' max='5' displayState=':= if(?advOptions,\"shown\",\"hidden\")' displayGroup='group"+modConfigName+"'>\n"
    indentLine += 1
    configScriptClose += indentText(indentLine)+"<Description> Frequency multiplier for "+modName+" "+oreName[currentOreGen]+" distributions </Description>\n"
    configScriptClose += indentText(indentLine)+"<DisplayName>"+modName+" "+oreName[currentOreGen]+" Freq.</DisplayName>\n"
    indentLine -= 1
    configScriptClose += indentText(indentLine)+"</OptionNumeric>\n"
    configScriptClose += indentText(indentLine)+"<OptionNumeric name='"+oreConfigName+"Size' default='1'  min='0' max='5' displayState=':= if(?advOptions,\"shown\",\"hidden\")' displayGroup='group"+modConfigName+"'>\n"
    indentLine += 1
    configScriptClose += indentText(indentLine)+"<Description> Size multiplier for "+modName+" "+oreName[currentOreGen]+" distributions </Description>\n"
    configScriptClose += indentText(indentLine)+"<DisplayName>"+modName+" "+oreName[currentOreGen]+" Size</DisplayName>\n"
    indentLine -= 1
    configScriptClose += indentText(indentLine)+"</OptionNumeric>\n"
          
    return configScriptOpen+configScriptList+configScriptClose

############## DETECT META NUMBER #################################
# If the meta number is anything other than zero, return the number
# Preceded by a colon.

def metaGen(currentMeta):
    if oreMeta[currentMeta] == '0':
        return ""
    else:
        return ":"+oreMeta[currentMeta]


################## INDIVIDUAL DISTRIBUTIONS ######################
# Each distribution is individually defined.

### Standard "Vanilla" Distribution

def vanillaDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    
    distText = indentText(indentLine)+"<StandardGen name='"+oreConfigName+str(level)+"Standard' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetStandardGen'>\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description> This mimics vanilla ore generation. </Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='Size' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='Frequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='Height' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel'/> \n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</StandardGen>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += vanillaDist(currentOreGen, 1)    
    return distText

### Layered Vein Distribution

def layeredVeinsDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Veins' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetLayeredVeins'>\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Small, fairly rare motherlodes with 2-4 horizontal veins each.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"'/> \n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += layeredVeinsDist(currentOreGen, 1)    
    return distText

### Vertical Vein Distribution

def verticalVeinsDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Veins' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetVerticalVeins'>\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Single vertical veins that occur with no motherlodes.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= 1.3 * "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += verticalVeinsDist(currentOreGen, 1)    
    return distText

### Small Deposit Distribution

def smallDepositsDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Veins' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetSmallDeposits'>\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Small motherlodes without any branches.\n"
    distText += indentText(indentLine)+"Similar to the deposits produced by StandardGen distributions.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += smallDepositsDist(currentOreGen, 1)    
    return distText

### Geode Distribution

def geodesDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    geodeSeed = "'0x"+randomHexNumber(4)+"'"
    
    #   Outer Crust
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Shell' block='"+orePipe[currentOreGen]+"' inherits='PresetSmallDeposits' seed="+geodeSeed+">\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"The geode's outer shell, composed of the Pipe material.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= 3 * "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Replaces block='minecraft:air'/>\n"
    distText += indentText(indentLine)+"<Replaces block='minecraft:water'/>\n"
    distText += indentText(indentLine)+"<Replaces block='minecraft:lava'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
 
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
            
    # Inner Crystals
    
    distText += indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Crystal' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetSmallDeposits' seed="+geodeSeed+">\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"The geode's inner material, usually some form of crystal.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= 1.5 * "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Replaces block='"+orePipe[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    #   Central Air Pocket
    
    distText += indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"AirBubble' block='minecraft:air' inherits='PresetSmallDeposits' seed="+geodeSeed+">\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"The air pocket within the center of a geode.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += geodesDist(currentOreGen, 1) 
      
    return distText

### Huge Vein Distribution

def hugeVeinsDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Veins' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetLayeredVeins'>\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Very large, extremely rare motherlodes.  Each motherlode has many long slender branches - so thin that\n"
    distText += indentText(indentLine)+"parts of the branch won't contain any ore at all.  This, combined with the incredible length of the\n"
    distText += indentText(indentLine)+"branches, makes them more challenging to follow underground.  Once found, however, a motherlode contains\n"
    distText += indentText(indentLine)+"enough ore to keep a player supplied for a very long time.\n"
    distText += indentText(indentLine)+"The rarity of these veins might be too frustrating in a single-player setting.  In SMP, though, teamwork \n"
    distText += indentText(indentLine)+"could make finding them much easier and the motherlodes are big enough to supply several people without\n"
    distText += indentText(indentLine)+"shortage.  This might be a good way to add challenge to multiplayer worlds.\n"
    distText += indentText(indentLine)+"Credit: based on feedback by dyrewulf from the MC forums.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += hugeVeinsDist(currentOreGen, 1)    
    return distText

### Sparse Vein Distribution

def sparseVeinsDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Veins' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetSparseVeins'>\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Large veins filled very lightly with ore.  Because they contain less ore per volume, \n"
    distText += indentText(indentLine)+"these veins are relatively wide and long.  Mining the ore from them is time consuming \n"
    distText += indentText(indentLine)+"compared to solid ore veins.  They are also more difficult to follow, since it is \n"
    distText += indentText(indentLine)+"harder to get an idea of their direction while mining.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' />\n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += sparseVeinsDist(currentOreGen, 1)    
    return distText

### Pipe Vein Distribution

def pipeVeinsDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    pipeSeed = "'0x"+randomHexNumber(4)+"'"
    
    # Ore
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Veins' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetPipeVeins' seed="+pipeSeed+">\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Short sparsely filled veins sloping up from near the bottom of the map.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' />\n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
    
    # Pipe Material
    
    distText += indentText(indentLine)+"<Veins name= '"+oreConfigName+str(level)+"Pipe' block='"+orePipe[currentOreGen]+"' inherits='PresetPipeVeins' seed="+pipeSeed+">\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Fills center of each tube with Pipe material.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= 0.5 * "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= 0.5 * "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' />\n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= 0.5 * "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= 0.5 * "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='OreDensity' avg='1' range='0'/>\n"
    distText += indentText(indentLine)+"<Replaces block='minecraft:dirt'/>\n"
    distText += indentText(indentLine)+"<Replaces block='minecraft:stone'/>\n"
    distText += indentText(indentLine)+"<Replaces block='minecraft:gravel'/>\n"
    distText += indentText(indentLine)+"<Replaces block='minecraft:netherrack'/>\n"
    distText += indentText(indentLine)+"<Replaces block='minecraft:end_stone'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += pipeVeinsDist(currentOreGen, 1)    
    return distText

### Compound Vein Distribution

def compoundVeinsDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    veinSeed = "'0x"+randomHexNumber(4)+"'"
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Veins' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetLayeredVeins' seed="+veinSeed+">\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Outer Vein consisting of \"ore\" material. \n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"Veins' block='"+orePipe[currentOreGen]+"' inherits='PresetLayeredVeins' seed="+veinSeed+">\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Inner vein consisting of a \"pipe\" material. \n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeSize' avg=':= 0.5 * "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Setting name='SegmentRadius' avg=':= 0.5 * "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += compoundVeinsDist(currentOreGen, 1)    
    return distText

### Strategic Cloud Distribution

def strategicCloudsDist(currentOreGen,level):
    orePreConfigName=modPrefix+oreName[currentOreGen]
    orePreBiomeName=oreBiomes[currentOreGen]
    orePrePreferName=orePreferBiomes[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    oreBiomeName=orePreBiomeName.replace(" ", "")
    orePreferName=orePrePreferName.replace(" ", "")
    global indentLine
    
    # Main Cloud
    
    distText = indentText(indentLine)+"<Cloud name='"+oreConfigName+str(level)+"Cloud' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetStrategicCloud'>\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Large irregular clouds filled lightly with ore.  These are huge, spanning several \n"
    distText += indentText(indentLine)+"adjacent chunks, and consequently rather rare.  They contain a sizeable amount of \n"
    distText += indentText(indentLine)+"ore, but it takes some time and effort to mine due to low density.\n"
    distText += indentText(indentLine)+"The intent for strategic clouds is that the player will need to actively search for\n"
    distText += indentText(indentLine)+"one and then set up a semi-permanent mining base and spend some time actually mining\n"
    distText += indentText(indentLine)+"the ore.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='DistributionFrequency' avg=':= "+oreFrequency[currentOreGen]+" * "+oreConfigName+"Freq *_default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='CloudRadius' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='CloudThickness' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"
    distText += indentText(indentLine)+"<Setting name='CloudHeight' avg='"+oreHeight[currentOreGen]+"' range='"+oreRange[currentOreGen]+"' type='normal' scaleTo='"+oreScale[currentOreGen]+"'/>\n"
    distText += indentText(indentLine)+"<Replaces block='"+oreReplace[currentOreGen]+"'/>\n"
    
    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Cloud>\n"
    
    # "Hint" Veins
    
    distText = indentText(indentLine)+"<Veins name='"+oreConfigName+str(level)+"HintVeins' block='"+oreBlock[currentOreGen]+metaGen(currentOreGen)+"' inherits='PresetHintVeins'>\n"
    indentLine += 1
    distText += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    distText += indentText(indentLine)+"Small, fairly rare motherlodes with 2-4 horizontal veins each.\n"
    indentLine -= 1
    distText += indentText(indentLine)+"</Description>\n"
    distText += indentText(indentLine)+"<DrawWireframe>:=drawWireframes</DrawWireframe>\n"
    distText += indentText(indentLine)+"<WireframeColor>"+oreWireframe[currentOreGen]+"</WireframeColor>\n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeFrequency' avg=':= 1.2 * _default_' range=':= _default_'/> \n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeHeight' avg=':= "+oreHeight[currentOreGen]+"/64 * dimension.groundLevel' range=':= "+oreRange[currentOreGen]+"/64 * dimension.groundLevel' type='normal' scaleTo='"+oreScale[currentOreGen]+"' /> \n"
    distText += indentText(indentLine)+"<Setting name='MotherlodeRangeLimit' avg=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_' range=':= "+oreSize[currentOreGen]+" * "+oreConfigName+"Size * _default_'/>\n"

    if level == 1:
        distText += biomeList(orePreferName)
    else:
        distText += biomeList(oreBiomeName)
    
    indentLine -= 1
    distText += indentText(indentLine)+"</Veins>\n"
        
    if orePreferBiomes[currentOreGen] != "NONE":
        if level == 0 :
            distText += strategicCloudsDist(currentOreGen, 1)    
    return distText

    

################# DISTRIBUTION SETUP #############################
# Sets up the actual ore distribution configuration for each type
# of distribution.

def distributionGen(currentOreGen, currentOrePreDist):
    global indentLine
    distributionText = ""
    orePreConfigName=modPrefix+oreName[currentOreGen]
    oreConfigName=orePreConfigName.replace(" ", "")
    currentOreDist=currentOrePreDist.replace(" ", "")
    
    if currentOreDist == 'Vanilla':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"vanillaStdGen\"'>\n"
        indentLine += 1
        distributionText += vanillaDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"
        
    elif currentOreDist == 'LayeredVeins':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"layeredVeins\"'>\n"
        indentLine += 1
        distributionText +=  layeredVeinsDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"
        
    elif currentOreDist == 'VerticalVeins':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"verticalVeins\"'>\n"
        indentLine += 1
        distributionText +=  verticalVeinsDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"

    elif currentOreDist == 'SmallDeposits':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"smallDeposits\"'>\n"
        indentLine += 1
        distributionText +=  smallDepositsDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"

    elif currentOreDist == 'Geodes':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"geodes\"'>\n"
        indentLine += 1
        distributionText +=  geodesDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"

    elif currentOreDist == 'HugeVeins':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"hugeVeins\"'>\n"
        indentLine += 1
        distributionText +=   hugeVeinsDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"

    elif currentOreDist == 'SparseVeins':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"sparseVeins\"'>\n"
        indentLine += 1
        distributionText +=   sparseVeinsDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"

    elif currentOreDist == 'PipeVeins':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"pipeVeins\"'>\n"
        indentLine += 1
        distributionText +=  pipeVeinsDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"

    elif currentOreDist == 'CompoundVeins':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"compoundVeins\"'>\n"
        indentLine += 1
        distributionText += compoundVeinsDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"

    elif currentOreDist == 'StrategicClouds':
        distributionText = indentText(indentLine)+"<IfCondition condition=':= "+oreConfigName+"Dist = \"strategicCloud\"'>\n"
        indentLine += 1
        distributionText +=  strategicCloudsDist(currentOreGen, 0)
        indentLine -= 1
        distributionText += indentText(indentLine)+"</IfCondition>\n"
        
    return distributionText
    

################## DISTRIBUTION SETUP ###############################
# Creates the entire distribution configuration section

def distConfigGen(currentOreGen, world):
    # Start with an empty script
    configScriptList = ""
    
    # The list of ore distributions will determine available options.
    distributionList = oreDistributions[currentOreGen]
    distributionList = distributionList.split(',')
    
    for distribution in distributionList:
        if oreWorld[currentOreGen] == world:
         configScriptList += distributionGen(currentOreGen, distribution)
             
    return configScriptList
    
##################### ORE WORLD CHECK ###############################
# Only returns anything if the ore is configured for the chosen world.

def worldCheck(currentOreGen, world):
    global indentLine    
    if oreWorld[currentOreGen] == world:
        return 1

####################### ORE REPLACEMENT CHECK #######################
# Only returns anything if the ore is configured to replace the
# chosen material.

def replaceCheck(currentOreGen, replace):
    global indentLine
    if oreReplace[currentOreGen] == replace:
        return 1

##################### Per-Material Ore Replacement #################
# Lists the vanilla ores to be replaced with the identified material.

def depositRemovalList(world, replacement):
    global indentLine
    outReplacement = ""
    availableOres = []
    replacementBlocks = []
    availableMetas = []
    availableBlocks = []
        
    for oreSelect in range(0, len(oreConfigName)):        
        if replaceCheck(oreSelect, replacement) == 1:
            availableOres.append(oreConfigName[oreSelect])
            availableBlocks.append(oreBlock[oreSelect])
            availableMetas.append(oreMeta[oreSelect])
            replacementBlocks.append(oreReplace[oreSelect])
            
    for availableSelect in range(0, len(availableOres)):
        outReplacement += indentText(indentLine)+"<Replaces block='"+availableBlocks[availableSelect]+":"+availableMetas[availableSelect]+"' />\n"
    
    return outReplacement


############## Remove Existing Ores ###############################
# Substitutes vanilla oregen with appropriate materials.

def depositRemoval(world):
    global indentLine
    replacementBlocks = []
    outConfig = ""
    
    # First, determine if anything needs to be replaced in this
    # world.
    
    # print oreConfigName
    
    for oreSelect in range(0, len(oreConfigName)):        
        if worldCheck(oreSelect, world) == 1:
            replacementBlocks.append(oreReplace[oreSelect])
            
    replaceList = list(set(replacementBlocks))
                
    outConfig += indentText(indentLine)+"<!-- **********   Vanilla Deposit Removal   ************* -->\n"
    
    for blockSelect in range (0, len(replaceList)): # list(set(replacementBlocks)) = remove duplicate blocks
        outConfig += indentText(indentLine)+"<Substitute name='"+modPrefix+world+"OreSubstitute"+str(blockSelect)+"' block='"+replaceList[blockSelect]+"'>\n"
        indentLine += 1
        outConfig += indentText(indentLine)+"<Description>\n"
        indentLine += 1
        outConfig += indentText(indentLine)+"Replace vanilla-generated ore clusters.\n"
        indentLine -= 1
        outConfig += indentText(indentLine)+"</Description>\n"
        outConfig += indentText(indentLine)+"<Comment>\n"
        indentLine += 1
        outConfig += indentText(indentLine)+"The global option deferredPopulationRange must be large enough to catch all ore clusters (>= 32).\n"
        indentLine -= 1
        outConfig += indentText(indentLine)+"</Comment>\n"
    
        outConfig += depositRemovalList(world,replaceList[blockSelect])
    
        indentLine -= 1
        outConfig += indentText(indentLine)+"</Substitute>\n"
            
        
    return outConfig
    

############################# MOD DETECTION ##########################
# If a mod is not installed, don't run the configuration.

def modDetectLevel():
    global indentLine
    indentLine=1

    if modDetect != "minecraft":
        outConfig = indentText(indentLine)+"<IfModInstalled name=\""+modDetect+"\">\n\n"
        indentLine += 1
        outConfig += indentText(indentLine)+"<ConfigSection>\n"
        indentLine += 1
        outConfig += configSetupSection()+"\n"
        outConfig += overworldSetupSection()+"\n"
        outConfig += netherSetupSection()+"\n"
        outConfig += endSetupSection()+"\n"
        indentLine -= 1
        outConfig += indentText(indentLine)+"</ConfigSection>\n"
        indentLine -= 1
        outConfig += indentText(indentLine)+"</IfModInstalled> \n "

        return outConfig
    else:
        outConfig = indentText(indentLine)+"<ConfigSection>\n "
        indentLine += 1
        outConfig += configSetupSection()+"\n"
        outConfig += overworldSetupSection()+"\n"
        outConfig += netherSetupSection()+"\n"
        outConfig += endSetupSection()+"\n\n"
        indentLine -= 1
        outConfig += indentText(indentLine)+"</ConfigSection>\n\n"
        
        return outConfig

############################# SETUP SCREEN ##########################
# Final configuration screen setup

def configSetupSection():
    global indentLine
    
    setupConfig = indentText(indentLine)+"<!-- Setup Screen Configuration -->\n\n"
    setupConfig += indentText(indentLine)+"<ConfigSection>\n"
    indentLine += 1
    setupConfig += indentText(indentLine)+"<OptionDisplayGroup name='group"+modConfigName+"' displayName='"+modName+" Ores' displayState='shown'> \n"
    indentLine += 1
    setupConfig += indentText(indentLine)+"<Description>\n"
    indentLine += 1
    setupConfig += indentText(indentLine)+"Distribution options for "+modName+" Ores.\n"
    indentLine -= 1
    setupConfig += indentText(indentLine)+"</Description>\n"
    indentLine -= 1
    setupConfig += indentText(indentLine)+"</OptionDisplayGroup>\n\n"
    
    for oreSelect in range (0, len(oreName)):
        setupConfig += indentText(indentLine)+"<ConfigSection>\n"
        indentLine += 1
        setupConfig += controlsGen(oreSelect)
        indentLine -= 1
        setupConfig += indentText(indentLine)+"</ConfigSection> \n"
    
    indentLine -= 1
    setupConfig += indentText(indentLine)+"</ConfigSection>\n\n"
    
    return setupConfig

################## OVERWORLD CONFIGURATION ##########################
# Final overworld setup (clean vanilla oregen, replace it with COG
# oregen)

def overworldSetupSection():
    global indentLine
    
    setupConfig = indentText(indentLine)+"<!-- Setup Overworld -->\n"
    setupConfig += indentText(indentLine)+"<IfCondition condition=':= ?COGActive'>\n"
    indentLine += 1
    setupConfig += depositRemoval("Overworld")
    setupConfig += indentText(indentLine)+"<!-- Adding ores --> \n"
               
    for oreSelect in range(0,len(oreName)):
        setupConfig+=distConfigGen(oreSelect, "Overworld")
    
    indentLine -= 1
    setupConfig += indentText(indentLine)+"</IfCondition>\n\n"
    
    return setupConfig
    
##################### NETHER CONFIGURATION ##########################
# Final nether setup (clean vanilla oregen, replace it with COG
# oregen)

def netherSetupSection():
    global indentLine
    verified = 0
    
    for oreSelect in range(0, len(oreConfigName)):    
            
        if oreWorld[oreSelect] == "Nether":
            verified = 1
            
    if verified == 0:
        return " "
    
    setupConfig = indentText(indentLine)+"<!-- Setup Nether -->\n"
    setupConfig += indentText(indentLine)+"<IfCondition condition=':= dimension.generator = \"HellRandomLevelSource\"'>\n"
    indentLine += 1
    setupConfig += depositRemoval("Nether")
    setupConfig += indentText(indentLine)+"<!-- Adding ores --> \n"
               
    for oreSelect in range(0,len(oreName)):
        setupConfig+=distConfigGen(oreSelect, "Nether")
    
    indentLine -= 1
    setupConfig += indentText(indentLine)+"</IfCondition>\n\n"
    
    return setupConfig

####################### END CONFIGURATION ##########################
# Final end setup (clean vanilla oregen, replace it with COG oregen)

def endSetupSection():
    global indentLine
    verified = 0
    
    for oreSelect in range(0, len(oreConfigName)):        
        if oreWorld[oreSelect] == "End":
            verified = 1
            
    if verified == 0:
        return " "
    
    setupConfig = indentText(indentLine)+"<!-- Setup End -->\n"
    setupConfig += indentText(indentLine)+"<IfCondition condition=':= dimension.generator = \"EndRandomLevelSource\"'>\n"
    indentLine += 1
    setupConfig += depositRemoval("End")
    setupConfig += indentText(indentLine)+"<!-- Adding ores --> \n"
               
    for oreSelect in range(0,len(oreName)):
        setupConfig+=distConfigGen(oreSelect, "End")
    
    indentLine -= 1
    setupConfig += indentText(indentLine)+"</IfCondition>\n\n"
    
    return setupConfig
    
############# ASSEMBLE CONFIGURATION ################################
# This is where the configuration gets prepared for writing.

def assembleConfig():
    
    configOutput = headerGen()
    configOutput += modDetectLevel()
    
    return configOutput

################ ERROR CHECK ########################################
# If an error was found, we do NOT want to overwrite the config file.

if errorCondition:
    sys.exit("Errors have occurred.  Nothing was written.\n")

################# WRITE CONFIG ######################################
# This is actually where the rubber meets the road; the configuration
# is written to an XML file.

xmlConfigFile = open('./'+modConfigName+'.xml', 'w+')
xmlConfigFile.write(assembleConfig())
