import sys
import os
import GUI_lib as glib
import Field_reconstruction.FR as fr
import numpy as np
from PIL import Image

workingDir=glib.currentFolder()
GUI=glib.Graphical_interface(designerFile=workingDir+'/Field_reconstruction/Direct_Propagation.ui')

#~~~~~~~~~~~~~~~~ Plot widgets ~~~~~~~~~~~~~~~~ 
graph=glib.mplFig(designerLayout=GUI.plotLayout)
graph.ax=graph.addAx(nrows=1,ncols=1)
graph.ax.set_xlabel('x (um)')
graph.ax.set_ylabel('y (um)')
graph.image=graph.ax.imshow([[0,0],[0,0]],cmap='Blues')



#~~~~~~~~~~~~~~~~ Shape widgets ~~~~~~~~~~~~~~~~ 
addFlakeButton=glib.button(designerWidget=GUI.addFlakeButton)
selectFlakeCombo=glib.comboBox(designerWidget=GUI.selectFlakeCombo)
selectFlakeCombo.addItem('Flake 1')
loadShapeButton=glib.button(designerWidget=GUI.loadShapeButton)
createShapeButton=glib.button(designerWidget=GUI.createShapeButton)
includeFlakeCheck=glib.checkBox(designerWidget=GUI.includeFlakeCheck)
includeFlakeCheck.setState(True)
magOriCombo=glib.comboBox(designerWidget=GUI.magOriCombo)
magOriCombo.addItems(['x','y','z','custom'])
magPhi=glib.lineEdit(designerWidget=GUI.magPhiLine,precision=2)
magTheta=glib.lineEdit(designerWidget=GUI.magThetaLine,precision=2)
magPhi.setEnabled(False)
magTheta.setEnabled(False)
Ms=glib.lineEdit(designerWidget=GUI.MsLine)


shapes=[fr.maskArray()]
shapeOris=[magOriCombo.text()]
shapePhis=[magPhi.getValue()]
shapeThetas=[magTheta.getValue()]
shapeMss=[Ms.getValue()]
shapeInclude=[includeFlakeCheck.state()]

def addFlakeButtonClicked():
    shapes.append(fr.maskArray())
    shapeOris.append(magOriCombo.text())
    shapePhis.append(magPhi.getValue())
    shapeThetas.append(magTheta.getValue())
    shapeMss.append(Ms.getValue())
    shapeInclude.append(includeFlakeCheck.state())
    selectFlakeCombo.addItem('Flake %i'%(len(shapes)))
    selectFlakeCombo.setIndex(len(shapes)-1)

def plotShape(shape):
    graph.clear()
    graph.ax=graph.addAx(nrows=1,ncols=1)
    graph.ax.set_xlabel('x (um)')
    graph.ax.set_ylabel('y (um)')
    graph.image=shape.plot(ax=graph.ax,show=False)
    setFigLxLy()
    graph.update()

def loadShape(filename):
    shape=shapes[selectFlakeCombo.index()]
    shape.load(filename)
    flakeName=filename.split('/')[-1].split('.')[0]
    plotShape(shape)

def loadShapeButtonClicked():     
    global workingDir
    filename,filter = glib.QFileDialog.getOpenFileName(parent=GUI.centralwidget,caption='Select shape file',directory=workingDir,filter='array (*.npy *.csv *.txt)')
    if filename=='':
        return
    workingDir=os.path.dirname(filename)
    loadShape(filename)

def magPhiAction():
    shapePhis[selectFlakeCombo.index()]=magPhi.getValue()

def magThetaAction():
    shapeThetas[selectFlakeCombo.index()]=magTheta.getValue()

def MsAction():
    shapeMss[selectFlakeCombo.index()]=Ms.getValue()

def includeFlakeCheckAction():
    shapeInclude[selectFlakeCombo.index()]=includeFlakeCheck.state()

def selectFlakeComboAction():
    i=selectFlakeCombo.index()
    magOriCombo.setIndex(shapeOris[i])
    magPhi.setValue(shapePhis[i])
    magTheta.setValue(shapeThetas[i])
    Ms.setValue(shapeMss[i])
    includeFlakeCheck.setState(shapeInclude[i])
    plotShape(shapes[i])

def createShapeButtonClicked():
    GUI_createShape.show()


def magOriAction():
    shapeOris[selectFlakeCombo.index()]=magOriCombo.text()
    magPhi.setEnabled(False)
    magTheta.setEnabled(False)
    if magOriCombo.text()=="x":
        magPhi.setValue(0)
        magTheta.setValue(90)
    elif magOriCombo.text()=="y":
        magPhi.setValue(90)
        magTheta.setValue(90)
    elif magOriCombo.text()=="z":
        magPhi.setValue(0)
        magTheta.setValue(0)
    elif magOriCombo.text()=="custom":
        magPhi.setEnabled(True)
        magTheta.setEnabled(True)
    magPhiAction()
    magThetaAction()



addFlakeButton.setAction(addFlakeButtonClicked)
selectFlakeCombo.setAction(selectFlakeComboAction)
loadShapeButton.setAction(loadShapeButtonClicked)
createShapeButton.setAction(createShapeButtonClicked)
magPhi.setAction(magPhiAction)
magTheta.setAction(magThetaAction)
Ms.setAction(MsAction)
includeFlakeCheck.setAction(includeFlakeCheckAction)
magOriCombo.setAction(magOriAction)

#~~~~~~~~~~~~~~~~ Dimensions widgets ~~~~~~~~~~~~~~~~

lx=glib.lineEdit(designerWidget=GUI.lxLine)
ly=glib.lineEdit(designerWidget=GUI.lyLine)
z=glib.lineEdit(designerWidget=GUI.zLine)
gaussianSmooth=glib.lineEdit(designerWidget=GUI.gaussianSmoothLine)


#Figure limits
def setFigLxLy():
    graph.image.set_extent([0,lx.getValue(),0,ly.getValue()])
    graph.update()
setFigLxLy()
lx.setAction(setFigLxLy)
ly.setAction(setFigLxLy)

#~~~~~~~~~~~~~~~~ Compute B ~~~~~~~~~~~~~~~~

computeBButton=glib.button(designerWidget=GUI.computeBButton)
def computeBClicked():
    for i in range(len(shapes)):
        if shapeInclude[i]:
            magArray=fr.homogeneous3dMag(shape=shapes[i],theta=shapeThetas[i],phi=shapePhis[i],Ms=shapeMss[i])
            break
    for j in range(i+1,len(shapes)):
        if shapeInclude[j]:
            if shapes[j].mask.shape!=shapes[i].mask.shape:
                raise ValueError('All shapes must have the same dimensions')
            magArray+=fr.homogeneous3dMag(shape=shapes[j],theta=shapeThetas[j],phi=shapePhis[j],Ms=shapeMss[j])
    global Bfield
    Bfield=fr.forwardPropagation(magArray=magArray,lx=lx.getValue()*1e3,ly=ly.getValue()*1e3,z=z.getValue(),gaussianSmooth=gaussianSmooth.getValue(),magUnit='muB')
    projectButton.setEnabled(True)
    projectBClicked()
computeBButton.setAction(computeBClicked)

#~~~~~~~~~~~~~~~~ Projection widgets ~~~~~~~~~~~~~~~~ 

projOriCombo=glib.comboBox(designerWidget=GUI.projOriCombo)
projPhi=glib.lineEdit(designerWidget=GUI.projPhiLine,precision=2)
projTheta=glib.lineEdit(designerWidget=GUI.projThetaLine,precision=2)
reverseProjButton=glib.button(designerWidget=GUI.reverseProjButton)
BminLine=glib.lineEdit(designerWidget=GUI.BminLine,precision=2)
BmaxLine=glib.lineEdit(designerWidget=GUI.BmaxLine,precision=2)
autoscaleButton=glib.button(designerWidget=GUI.autoscaleButton)
centerZeroFieldButton=glib.button(designerWidget=GUI.centerZeroFieldButton)
projectButton=glib.button(designerWidget=GUI.projectButton)
projectButton.setEnabled(False)
saveProjButton=glib.button(designerWidget=GUI.saveProjButton)

#Orientation
projOriCombo.addItems(['x','y','z','NV1','NV2','NV3','NV4'])
def projOriAction():
    if projOriCombo.text()=="x":
        projPhi.setValue(0)
        projTheta.setValue(90)
    elif projOriCombo.text()=="y":
        projPhi.setValue(90)
        projTheta.setValue(90)
    elif projOriCombo.text()=="z":
        projPhi.setValue(0)
        projTheta.setValue(0)
    elif projOriCombo.text()=="NV1":
        projPhi.setValue(0)
        projTheta.setValue(54.7)
    elif projOriCombo.text()=="NV2":
        projPhi.setValue(90)
        projTheta.setValue(54.7)
    elif projOriCombo.text()=="NV3":
        projPhi.setValue(180)
        projTheta.setValue(54.7)
    elif projOriCombo.text()=="NV4":
        projPhi.setValue(270)
        projTheta.setValue(54.7)
    if projectButton.isEnabled():
        projectBClicked()
projOriCombo.setAction(projOriAction)

def reverseProjButtonClicked():
    projPhi.setValue((projPhi.getValue()+180)%360)
    projTheta.setValue((180-projTheta.getValue()))
    if projectButton.isEnabled():
        projectBClicked()
reverseProjButton.setAction(reverseProjButtonClicked)


#B limits
def setBlims():
    graph.image.set_clim(vmin=BminLine.getValue(),vmax=BmaxLine.getValue())
    graph.update()
BminLine.setAction(setBlims)
BmaxLine.setAction(setBlims)


def autoscaleButtonClicked():
    BminLine.setValue(np.min(graph.ax.images[0].get_array()))
    BmaxLine.setValue(np.max(graph.ax.images[0].get_array()))  
    setBlims()
autoscaleButton.setAction(autoscaleButtonClicked)

def centerZeroFieldButtonClicked():
    BminLine.setValue(-np.max(np.abs(graph.ax.images[0].get_array())))
    BmaxLine.setValue(np.max(np.abs(graph.ax.images[0].get_array())))  
    setBlims()
centerZeroFieldButton.setAction(centerZeroFieldButtonClicked)

#Project B
def projectBClicked():
    graph.clear()
    graph.ax=graph.addAx(nrows=1,ncols=1)
    graph.ax.set_xlabel('x (um)')
    graph.ax.set_ylabel('y (um)')
    image,cbar=Bfield.plotFieldProjection(theta=projTheta.getValue(),phi=projPhi.getValue(),ax=graph.ax,show=False)
    cbar.set_label('B (G)')
    graph.image=image
    setFigLxLy()
    centerZeroFieldButtonClicked()
    graph.update()  
projectButton.setAction(projectBClicked)

#Save projection
def saveProjButtonClicked():
    global workingDir
    filename,filter = glib.QFileDialog.getSaveFileName(parent=GUI.centralwidget, caption='Save file', directory=workingDir, filter='numpy (*.npy);;csv (*.csv);;txt (*.txt))',initialFilter='csv (*.csv)')
    if filename=='':
        return
    workingDir=os.path.dirname(filename)
    extension=filter.split('*')[1].split(')')[0]
    if not filename.endswith(extension):
        filename+=extension
    np.savetxt(filename,graph.ax.images[0].get_array(),delimiter=',')
    imageName=filename.split('.')[0]+'.png'
    graph.fig.savefig(imageName)
saveProjButton.setAction(saveProjButtonClicked)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create shape window ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GUI_createShape=glib.Graphical_interface(designerFile=workingDir+'/Field_reconstruction/Create_shape.ui',parent=GUI)

loadCanvasButton=glib.button(designerWidget=GUI_createShape.loadCanvasButton)
makeCanvasButton=glib.button(designerWidget=GUI_createShape.makeCanvasButton)
linenx=glib.lineEdit(designerWidget=GUI_createShape.linenx)
lineny=glib.lineEdit(designerWidget=GUI_createShape.lineny)
linenxmax=glib.lineEdit(designerWidget=GUI_createShape.linenxmax)
linenymax=glib.lineEdit(designerWidget=GUI_createShape.linenymax)
linenxmin=glib.lineEdit(designerWidget=GUI_createShape.linenxmin)
linenymin=glib.lineEdit(designerWidget=GUI_createShape.linenymin)
resizeResetButton=glib.button(designerWidget=GUI_createShape.resizeResetButton)
restartButton=glib.button(designerWidget=GUI_createShape.restartButton)
finishButton=glib.button(designerWidget=GUI_createShape.finishButton)
saveShapeButton=glib.button(designerWidget=GUI_createShape.saveShapeButton)

shapeGraph=glib.mplFig(designerLayout=GUI_createShape.plotLayout)

createShapeMask=fr.maskArray()

#Loading Canvas

def loadCanvasAction():
    global workingDir
    filename,filter = glib.QFileDialog.getOpenFileName(parent=GUI_createShape,caption='Select canvas file',directory=workingDir,filter='all supported files (*.npy *.csv *.txt *.png *.jpg *.mat)')
    if filename=='':
        return
    workingDir=os.path.dirname(filename)
    shapeGraph.clear()
    if filename[-4:]=='.npy':
        baseArray = np.load(filename)
    elif filename[-4:]=='.csv' or filename[-4:]=='.txt' :
        baseArray = np.loadtxt(filename,delimiter=',',dtype=int)
    elif filename[-4:]=='.png' or filename[-4:]=='.jpg':
        baseArray = np.array(Image.open(filename))
        baseArray=np.flipud(baseArray)
    elif filename[-4:]=='.mat':
        import Mat_data_processing as mdp
        m=mdp.matFile(filename)
        if m.matKeys[3]=='smNVscan' :
            matFile=mdp.NVAFM_scan_matFile(filename)
            baseArray=matFile.dataDic['Counter1 forward']
        elif m.matKeys[3]=='smNVscan_new' :
            matFile=mdp.NVAFM_RFscan_matFile(filename)
            baseArray=matFile.ESRMap()
    createShapeMask.create(baseArray=baseArray,fig=shapeGraph.fig)   
    resizeResetButtonAction()
loadCanvasButton.setAction(loadCanvasAction)

def makeCanvasAction():
    createShapeMask.create(baseArray=np.zeros((linenx.getValue(),lineny.getValue())),fig=shapeGraph.fig)
    resizeResetButtonAction()
makeCanvasButton.setAction(makeCanvasAction)


# Resizing

def resizeAction():
    createShapeMask.ax.set_xlim([linenxmin.getValue(),linenxmax.getValue()])
    createShapeMask.ax.set_ylim([linenymin.getValue(),linenymax.getValue()])
    createShapeMask.fig.canvas.draw()
linenxmin.setAction(resizeAction)
linenxmax.setAction(resizeAction)
linenymin.setAction(resizeAction)
linenymax.setAction(resizeAction)

def resizeResetButtonAction():
    linenx.setValue(createShapeMask.mask.shape[0])
    lineny.setValue(createShapeMask.mask.shape[1])  
    linenxmax.setValue(createShapeMask.mask.shape[1])
    linenymax.setValue(createShapeMask.mask.shape[0])
    resizeAction()
resizeResetButton.setAction(resizeResetButtonAction)

#Drawing shape

def restartButtonAction():
    createShapeMask.restart()
restartButton.setAction(restartButtonAction)

def finishButtonAction():
    createShapeMask.fillMask()
finishButton.setAction(finishButtonAction)

#Saving

def saveButtonAction():
    global workingDir
    filename,filter = glib.QFileDialog.getSaveFileName(parent=GUI_createShape, caption='Save file', directory=workingDir, filter='numpy (*.npy);;csv (*.csv);;txt (*.txt))',initialFilter='csv (*.csv)')
    if filename=='':
        return
    workingDir=os.path.dirname(filename)
    extension=filter.split('*')[1].split(')')[0]
    if not filename.endswith(extension):
        filename+=extension  
    data=createShapeMask.mask[linenymin.getValue():linenymax.getValue(),linenxmin.getValue():linenxmax.getValue()] 
    if filename[-4:]=='.npy':
            np.save(filename,data)
    elif filename[-4:]=='.csv':
        np.savetxt(filename,data,delimiter=',',fmt='%i')
    elif filename[-4:]=='.txt':
        np.savetxt(filename,data,delimiter=' ',fmt='%i')
    GUI_createShape.close()
    loadShape(filename)
saveShapeButton.setAction(saveButtonAction)

GUI.show()
glib.qapp.exec_()