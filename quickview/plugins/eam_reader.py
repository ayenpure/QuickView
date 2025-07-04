from paraview.util.vtkAlgorithm import *
from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.vtkCommonCore import vtkPoints, vtkIdTypeArray, vtkDataArraySelection
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, vtkCellArray
from vtkmodules.util import vtkConstants, numpy_support
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridWriter
from paraview import print_error

try:
    import netCDF4
    import numpy as np

    _has_deps = True
except ImportError as ie:
    print_error(
        "Missing required Python modules/packages. Algorithms in this module may "
        "not work as expected! \n {0}".format(ie)
    )
    _has_deps = False

dims1 = set(["ncol"])
dims2 = set(["time", "ncol"])
dims3i = set(["time", "ilev", "ncol"])
dims3m = set(["time", "lev", "ncol"])


class EAMConstants:
    LEV = "lev"
    HYAM = "hyam"
    HYBM = "hybm"
    ILEV = "ilev"
    HYAI = "hyai"
    HYBI = "hybi"
    P0 = float(1e5)
    PS0 = float(1e5)


from enum import Enum


class VarType(Enum):
    _1D = 1
    _2D = 2
    _3Dm = 3
    _3Di = 4


class VarMeta:
    def __init__(self, name, info):
        self.name = name
        self.type = None
        self.transpose = False
        self.fillval = np.nan

        dims = info.dimensions

        if len(dims) == 1:
            self.type = VarType._1D
        elif len(dims) == 2:
            self.type = VarType._2D
        elif len(dims) == 3:
            if "lev" in dims:
                self.type = VarType._3Dm
            elif "ilev" in dims:
                self.type = VarType._3Di

            if "ncol" in dims[1]:
                self.transpose = True


def compare(data, arrays, dim):
    ref = data[arrays[0]][:].flatten()
    if len(ref) != dim:
        raise Exception(
            "Length of hya_/hyb_ variable does not match the corresponding dimension"
        )
    for i, array in enumerate(arrays[1:], start=1):
        comp = data[array][:].flatten()
        if not np.array_equal(ref, comp):
            return None
    return ref


def FindSpecialVariable(data, lev, hya, hyb):
    dim = data.dimensions.get(lev, None)
    if dim is None:
        raise Exception(f"{lev} not found in dimensions")
    dim = dim.size
    var = np.array(list(data.variables.keys()))

    if lev in var:
        lev = data[lev][:].flatten()
        return lev

    from numpy.core.defchararray import find

    _hyai = var[find(var, hya) != -1]
    _hybi = var[find(var, hyb) != -1]
    if len(_hyai) != len(_hybi):
        raise Exception(f"Unmatched pair of hya and hyb variables found")

    p0 = EAMConstants.P0
    ps0 = EAMConstants.PS0

    if len(_hyai) == 1:
        hyai = data[_hyai[0]][:].flatten()
        hybi = data[_hyai[1]][:].flatten()
        if not (len(hyai) == dim and len(hybi) == dim):
            raise Exception(
                f"Lengths of arrays for hya_ and hyb_ variables do not match"
            )
        ldata = ((hyai * p0) + (hybi * ps0)) / 100.0
        return ldata
    else:
        hyai = compare(data, _hyai, dim)
        hybi = compare(data, _hybi, dim)
        if hyai is None or hybi is None:
            raise Exception(f"Values within hya_ and hyb_ arrays do not match")
        else:
            ldata = ((hyai * p0) + (hybi * ps0)) / 100.0
            return ldata


# ------------------------------------------------------------------------------
# A reader example.
# ------------------------------------------------------------------------------
def createModifiedCallback(anobject):
    import weakref

    weakref_obj = weakref.ref(anobject)
    anobject = None

    def _markmodified(*args, **kwars):
        o = weakref_obj()
        if o is not None:
            o.Modified()

    return _markmodified


@smproxy.reader(
    name="EAMSource",
    label="EAM Data Reader",
    extensions="nc",
    file_description="NETCDF files for EAM",
)
@smproperty.xml("""<OutputPort name="2D"  index="0" />""")
@smproperty.xml("""<OutputPort name="3D middle layer"  index="1" />""")
@smproperty.xml("""<OutputPort name="3D interface layer"  index="2" />""")
@smproperty.xml(
    """
                <StringVectorProperty command="SetDataFileName"
                      name="FileName1"
                      label="Data File"
                      number_of_elements="1">
                    <FileListDomain name="files" />
                    <Documentation>Specify the NetCDF data file name.</Documentation>
                </StringVectorProperty>
                """
)
@smproperty.xml(
    """
                <StringVectorProperty command="SetConnFileName"
                      name="FileName2"
                      label="Connectivity File"
                      number_of_elements="1">
                    <FileListDomain name="files" />
                    <Documentation>Specify the NetCDF connecticity file name.</Documentation>
                </StringVectorProperty>
                """
)
class EAMSource(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=0, nOutputPorts=3, outputType="vtkUnstructuredGrid"
        )
        self._DataFileName = None
        self._ConnFileName = None
        # Variables for dimension sliders
        self._time = 0
        self._lev = 0
        self._ilev = 0
        # Arrays to store field names in netCDF file
        self._vars1D = []
        self._vars2D = []
        self._vars3Di = []
        self._vars3Dm = []
        self._timeSteps = []

        # vtkDataArraySelection to allow users choice for fields
        # to fetch from the netCDF data set
        self._vars1Darr = vtkDataArraySelection()
        self._vars2Darr = vtkDataArraySelection()
        self._vars3Diarr = vtkDataArraySelection()
        self._vars3Dmarr = vtkDataArraySelection()
        # Cache for non temporal variables
        # Store { names : data }
        self._vars1DCacahe = {}
        # Add observers for the selection arrays
        self._vars1Darr.AddObserver("ModifiedEvent", createModifiedCallback(self))
        self._vars2Darr.AddObserver("ModifiedEvent", createModifiedCallback(self))
        self._vars3Diarr.AddObserver("ModifiedEvent", createModifiedCallback(self))
        self._vars3Dmarr.AddObserver("ModifiedEvent", createModifiedCallback(self))

        # Storing Area as FieldData if available in file
        self._areavar = False

    # Method to clear all the variable names
    def _clear(self):
        self._vars1D.clear()
        self._vars2D.clear()
        self._vars3Di.clear()
        self._vars3Dm.clear()

    def _populate_variable_metadata(self):
        if self._DataFileName is None:
            return
        vardata = netCDF4.Dataset(self._DataFileName, "r")
        for name, info in vardata.variables.items():
            if "ncol_d" in info.dimensions:
                continue
            varmeta = VarMeta(name, info)
            if varmeta.type == VarType._1D:
                self._vars1D.append(varmeta)
                if name == "area":
                    self._areavar = True
            elif varmeta.type == VarType._2D:
                self._vars2D.append(varmeta)
                self._vars2Darr.AddArray(name)
            elif varmeta.type == VarType._3Di:
                self._vars3Di.append(varmeta)
                self._vars3Diarr.AddArray(name)
            elif varmeta.type == VarType._3Dm:
                self._vars3Dm.append(varmeta)
                self._vars3Dmarr.AddArray(name)
            try:
                fillval = info.getncattr("_FillValue")
                varmeta.fillval = fillval
            except Exception as e:
                traceback.print_exc()
                pass
        self._vars2Darr.DisableAllArrays()
        self._vars3Diarr.DisableAllArrays()
        self._vars3Dmarr.DisableAllArrays()
        timesteps = vardata["time"][:].data.flatten()
        self._timeSteps.extend(timesteps)
        self.timeDim = vardata.dimensions["time"].size
        self.ilevDim = vardata.dimensions["ilev"].size
        self.levDim = vardata.dimensions["lev"].size

    def SetDataFileName(self, fname):
        if fname is not None and fname != "None":
            if fname != self._DataFileName:
                self._DataFileName = fname
                self._clear()
                self._populate_variable_metadata()
                self.Modified()

    def SetConnFileName(self, fname):
        if fname != self._ConnFileName:
            self._ConnFileName = fname
            self.Modified()

    @smproperty.doublevector(
        name="TimestepValues", information_only="1", si_class="vtkSITimeStepsProperty"
    )
    def GetTimestepValues(self):
        return self._timeSteps

    # Array selection API is typical with readers in VTK
    # This is intended to allow ability for users to choose which arrays to
    # load. To expose that in ParaView, simply use the
    # smproperty.dataarrayselection().
    # This method **must** return a `vtkDataArraySelection` instance.
    @smproperty.dataarrayselection(name="2D Variables")
    def Get2DDataArrays(self):
        return self._vars2Darr

    @smproperty.dataarrayselection(name="3D Middle Layer Variables")
    def Get3DmDataArrays(self):
        return self._vars3Dmarr

    @smproperty.dataarrayselection(name="3D Interface Layer Variables")
    def Get3DiDataArrays(self):
        return self._vars3Diarr

    def RequestInformation(self, request, inInfo, outInfo):
        executive = self.GetExecutive()
        for i in range(3):
            port = outInfo.GetInformationObject(i)
            port.Remove(executive.TIME_STEPS())
            port.Remove(executive.TIME_RANGE())
            if self._timeSteps is not None and len(self._timeSteps) > 0:
                for t in self._timeSteps:
                    port.Append(executive.TIME_STEPS(), t)
                port.Append(executive.TIME_RANGE(), self._timeSteps[0])
                port.Append(executive.TIME_RANGE(), self._timeSteps[-1])
        return 1

    # TODO : implement request extents
    def RequestUpdateExtent(self, request, inInfo, outInfo):
        return super().RequestUpdateExtent(request, inInfo, outInfo)

    def GetTimeIndex(self, time):
        timeInd = 0
        if self._timeSteps != None and len(self._timeSteps) > 1:
            for t in self._timeSteps[1:]:
                if time == t:
                    break
                else:
                    timeInd = timeInd + 1
            return timeInd
        return 0

    def RequestData(self, request, inInfo, outInfo):
        if (
            self._ConnFileName is None
            or self._ConnFileName == "None"
            or self._DataFileName is None
            or self._DataFileName == "None"
        ):
            print_error(
                "Either one or both, the data file or connectivity file, are not provided!"
            )
            return 0
        global _has_deps
        if not _has_deps:
            print_error("Required Python module 'netCDF4' or 'numpy' missing!")
            return 0

        executive = self.GetExecutive()
        from_port = request.Get(executive.FROM_OUTPUT_PORT())
        timeInfo = outInfo.GetInformationObject(from_port)
        timeInd = 0
        if timeInfo.Has(executive.UPDATE_TIME_STEP()) and len(self._timeSteps) > 0:
            time = timeInfo.Get(executive.UPDATE_TIME_STEP())
            timeInd = self.GetTimeIndex(time)

        meshdata = netCDF4.Dataset(self._ConnFileName, "r")
        vardata = netCDF4.Dataset(self._DataFileName, "r")

        lat = meshdata["cell_corner_lat"][:].data.flatten()
        lon = meshdata["cell_corner_lon"][:].data.flatten()

        output2D = dsa.WrapDataObject(vtkUnstructuredGrid.GetData(outInfo, 0))
        output3Dm = dsa.WrapDataObject(vtkUnstructuredGrid.GetData(outInfo, 1))
        output3Di = dsa.WrapDataObject(vtkUnstructuredGrid.GetData(outInfo, 2))

        coords = np.empty((len(lat), 3), dtype=np.float64)
        coords[:, 0] = lon
        coords[:, 1] = lat
        coords[:, 2] = 0.0
        _coords = dsa.numpyTovtkDataArray(coords)
        vtk_coords = vtkPoints()
        vtk_coords.SetData(_coords)
        output2D.SetPoints(vtk_coords)

        ncells2D = meshdata["cell_corner_lat"][:].data.shape[0]
        cellTypes = np.empty(ncells2D, dtype=np.uint8)
        offsets = np.arange(0, (4 * ncells2D) + 1, 4, dtype=np.int64)
        cells = np.arange(ncells2D * 4, dtype=np.int64)
        cellTypes.fill(vtkConstants.VTK_QUAD)
        cellTypes = numpy_support.numpy_to_vtk(
            num_array=cellTypes.ravel(),
            deep=True,
            array_type=vtkConstants.VTK_UNSIGNED_CHAR,
        )
        offsets = numpy_support.numpy_to_vtk(
            num_array=offsets.ravel(), deep=True, array_type=vtkConstants.VTK_ID_TYPE
        )
        cells = numpy_support.numpy_to_vtk(
            num_array=cells.ravel(), deep=True, array_type=vtkConstants.VTK_ID_TYPE
        )
        cellArray = vtkCellArray()
        cellArray.SetData(offsets, cells)
        output2D.VTKObject.SetCells(cellTypes, cellArray)

        gridAdapter2D = dsa.WrapDataObject(output2D)
        for varmeta in self._vars2D:
            if self._vars2Darr.ArrayIsEnabled(varmeta.name):
                data = vardata[varmeta.name][:].data[timeInd].flatten()
                data = np.where(data == varmeta.fillval, np.nan, data)
                gridAdapter2D.CellData.append(data, varmeta.name)

        lev = None
        try:
            lev = FindSpecialVariable(
                vardata, EAMConstants.LEV, EAMConstants.HYAM, EAMConstants.HYBM
            )
            if not lev is None:
                coords3Dm = np.empty((self.levDim, len(lat), 3), dtype=np.float64)
                levInd = 0
                for z in lev:
                    coords = np.empty((len(lat), 3), dtype=np.float64)
                    coords[:, 0] = lon
                    coords[:, 1] = lat
                    coords[:, 2] = z
                    coords3Dm[levInd] = coords
                    levInd = levInd + 1
                coords3Dm = coords3Dm.flatten().reshape(self.levDim * len(lat), 3)
                _coords = dsa.numpyTovtkDataArray(coords3Dm)
                vtk_coords = vtkPoints()
                vtk_coords.SetData(_coords)
                output3Dm.SetPoints(vtk_coords)
                cellTypesm = np.empty(ncells2D * self.levDim, dtype=np.uint8)
                offsetsm = np.arange(
                    0, (4 * ncells2D * self.levDim) + 1, 4, dtype=np.int64
                )
                cellsm = np.arange(ncells2D * self.levDim * 4, dtype=np.int64)
                cellTypesm.fill(vtkConstants.VTK_QUAD)
                cellTypesm = numpy_support.numpy_to_vtk(
                    num_array=cellTypesm.ravel(),
                    deep=True,
                    array_type=vtkConstants.VTK_UNSIGNED_CHAR,
                )
                offsetsm = numpy_support.numpy_to_vtk(
                    num_array=offsetsm.ravel(),
                    deep=True,
                    array_type=vtkConstants.VTK_ID_TYPE,
                )
                cellsm = numpy_support.numpy_to_vtk(
                    num_array=cellsm.ravel(),
                    deep=True,
                    array_type=vtkConstants.VTK_ID_TYPE,
                )
                cellArraym = vtkCellArray()
                cellArraym.SetData(offsetsm, cellsm)
                output3Dm.VTKObject.SetCells(cellTypesm, cellArraym)

                gridAdapter3Dm = dsa.WrapDataObject(output3Dm)
                for varmeta in self._vars3Dm:
                    if self._vars3Dmarr.ArrayIsEnabled(varmeta.name):
                        if not varmeta.transpose:
                            data = vardata[varmeta.name][:].data[timeInd].flatten()
                        else:
                            data = (
                                vardata[varmeta.name][:]
                                .data[timeInd]
                                .transpose()
                                .flatten()
                            )
                        data = np.where(data == varmeta.fillval, np.nan, data)
                        gridAdapter3Dm.CellData.append(data, varmeta.name)
                gridAdapter3Dm.FieldData.append(self.levDim, "numlev")
                gridAdapter3Dm.FieldData.append(lev, "lev")
        except Exception as e:
            print_error("Error occurred while processing middle layer variables :", e)

        ilev = None
        try:
            ilev = FindSpecialVariable(
                vardata, EAMConstants.ILEV, EAMConstants.HYAI, EAMConstants.HYBI
            )
            if not ilev is None:
                coords3Di = np.empty((self.ilevDim, len(lat), 3), dtype=np.float64)
                ilevInd = 0
                for z in ilev:
                    coords = np.empty((len(lat), 3), dtype=np.float64)
                    coords[:, 0] = lon
                    coords[:, 1] = lat
                    coords[:, 2] = z
                    coords3Di[ilevInd] = coords
                    ilevInd = ilevInd + 1
                coords3Di = coords3Di.flatten().reshape(self.ilevDim * len(lat), 3)
                _coords = dsa.numpyTovtkDataArray(coords3Di)
                vtk_coords = vtkPoints()
                vtk_coords.SetData(_coords)
                output3Di.SetPoints(vtk_coords)
                cellTypesi = np.empty(ncells2D * self.ilevDim, dtype=np.uint8)
                offsetsi = np.arange(
                    0, (4 * ncells2D * self.ilevDim) + 1, 4, dtype=np.int64
                )
                cellsi = np.arange(ncells2D * self.ilevDim * 4, dtype=np.int64)
                cellTypesi.fill(vtkConstants.VTK_QUAD)
                cellTypesi = numpy_support.numpy_to_vtk(
                    num_array=cellTypesi.ravel(),
                    deep=True,
                    array_type=vtkConstants.VTK_UNSIGNED_CHAR,
                )
                offsetsi = numpy_support.numpy_to_vtk(
                    num_array=offsetsi.ravel(),
                    deep=True,
                    array_type=vtkConstants.VTK_ID_TYPE,
                )
                cellsi = numpy_support.numpy_to_vtk(
                    num_array=cellsi.ravel(),
                    deep=True,
                    array_type=vtkConstants.VTK_ID_TYPE,
                )
                cellArrayi = vtkCellArray()
                cellArrayi.SetData(offsetsi, cellsi)
                output3Di.VTKObject.SetCells(cellTypesi, cellArrayi)

                gridAdapter3Di = dsa.WrapDataObject(output3Di)
                for varmeta in self._vars3Di:
                    if self._vars3Diarr.ArrayIsEnabled(varmeta.name):
                        if not varmeta.transpose:
                            data = vardata[varmeta.name][:].data[timeInd].flatten()
                        else:
                            data = (
                                vardata[varmeta.name][:]
                                .data[timeInd]
                                .transpose()
                                .flatten()
                            )
                        data = np.where(data == varmeta.fillval, np.nan, data)
                        gridAdapter3Di.CellData.append(data, varmeta.name)
                gridAdapter3Di.FieldData.append(self.ilevDim, "numilev")
                gridAdapter3Di.FieldData.append(ilev, "ilev")
        except Exception as e:
            print_error(
                "Error occurred while processing interface layer variables :", e
            )

        return 1


import traceback


@smproxy.reader(
    name="EAMSliceSource",
    label="EAM Slice Data Reader",
    extensions="nc",
    file_description="NETCDF files for EAM",
)
@smproperty.xml("""<OutputPort name="2D"  index="0" />""")
@smproperty.xml(
    """
                <StringVectorProperty command="SetDataFileName"
                      name="FileName1"
                      label="Data File"
                      number_of_elements="1">
                    <FileListDomain name="files" />
                    <Documentation>Specify the NetCDF data file name.</Documentation>
                </StringVectorProperty>
                """
)
@smproperty.xml(
    """
                <StringVectorProperty command="SetConnFileName"
                      name="FileName2"
                      label="Connectivity File"
                      number_of_elements="1">
                    <FileListDomain name="files" />
                    <Documentation>Specify the NetCDF connecticity file name.</Documentation>
                </StringVectorProperty>
                """
)
@smproperty.xml(
    """
                <IntVectorProperty name="Middle Layer"
                    command="SetMiddleLayer"
                    number_of_elements="1"
                    default_values="0">
                </IntVectorProperty>
                """
)
@smproperty.xml(
    """
                <IntVectorProperty name="Interface Layer"
                    command="SetInterfaceLayer"
                    number_of_elements="1"
                    default_values="0">
                </IntVectorProperty>
                """
)
class EAMSliceSource(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(
            self, nInputPorts=0, nOutputPorts=1, outputType="vtkUnstructuredGrid"
        )
        self._output = vtkUnstructuredGrid()

        self._DataFileName = None
        self._ConnFileName = None
        self._dirty = False
        self._2d_update = True
        self._lev_update = True
        self._ilev_update = True

        # Variables for dimension sliders
        self._time = 0
        self._lev = 0
        self._ilev = 0
        # Arrays to store field names in netCDF file
        self._vars1D = []
        self._vars2D = []
        self._vars3Di = []
        self._vars3Dm = []
        self._timeSteps = []

        # vtkDataArraySelection to allow users choice for fields
        # to fetch from the netCDF data set
        self._vars1Darr = vtkDataArraySelection()
        self._vars2Darr = vtkDataArraySelection()
        self._vars3Diarr = vtkDataArraySelection()
        self._vars3Dmarr = vtkDataArraySelection()
        # Cache for non temporal variables
        # Store { names : data }
        self._vars1DCacahe = {}
        # Add observers for the selection arrays
        self._vars1Darr.AddObserver("ModifiedEvent", createModifiedCallback(self))
        self._vars2Darr.AddObserver("ModifiedEvent", createModifiedCallback(self))
        self._vars3Diarr.AddObserver("ModifiedEvent", createModifiedCallback(self))
        self._vars3Dmarr.AddObserver("ModifiedEvent", createModifiedCallback(self))
        # Flag for area var to calculate averages
        self._areavar = None

    # Method to clear all the variable names
    def _clear(self):
        self._vars1D.clear()
        self._vars2D.clear()
        self._vars3Di.clear()
        self._vars3Dm.clear()

    def _populate_variable_metadata(self):
        if self._DataFileName is None:
            return
        vardata = netCDF4.Dataset(self._DataFileName, "r")
        for name, info in vardata.variables.items():
            dims = set(info.dimensions)
            if not (dims == dims1 or dims == dims2 or dims == dims3m or dims == dims3i):
                continue
            varmeta = VarMeta(name, info)
            if varmeta.type == VarType._1D:
                self._vars1D.append(varmeta)
                if "area" in name:
                    self._areavar = varmeta
            elif varmeta.type == VarType._2D:
                self._vars2D.append(varmeta)
                self._vars2Darr.AddArray(name)
            elif varmeta.type == VarType._3Dm:
                self._vars3Dm.append(varmeta)
                self._vars3Dmarr.AddArray(name)
            elif varmeta.type == VarType._3Di:
                self._vars3Di.append(varmeta)
                self._vars3Diarr.AddArray(name)
            try:
                fillval = info.getncattr("_FillValue")
                varmeta.fillval = fillval
            except Exception as e:
                pass
        self._vars2Darr.DisableAllArrays()
        self._vars3Diarr.DisableAllArrays()
        self._vars3Dmarr.DisableAllArrays()

        timesteps = vardata["time"][:].data.flatten()
        self._timeSteps.extend(timesteps)

    def SetDataFileName(self, fname):
        if fname is not None and fname != "None":
            if fname != self._DataFileName:
                self._DataFileName = fname
                self._dirty = True
                self._2d_update = True
                self._lev_update = True
                self._ilev_update = True
                self._clear()
                self._populate_variable_metadata()
                self.Modified()

    def SetConnFileName(self, fname):
        if fname != self._ConnFileName:
            self._ConnFileName = fname
            self._dirty = True
            self._2d_update = True
            self._lev_update = True
            self._ilev_update = True
            self.Modified()

    def SetMiddleLayer(self, lev):
        if self._lev != lev:
            self._lev = lev
            self._lev_update = True
            self.Modified()

    def SetInterfaceLayer(self, ilev):
        if self._ilev != ilev:
            self._ilev = ilev
            self._ilev_update = True
            self.Modified()

    def SetCalculateAverages(self, calcavg):
        if self._avg != calcavg:
            self._avg = calcavg
            self.Modified()

    @smproperty.doublevector(
        name="TimestepValues", information_only="1", si_class="vtkSITimeStepsProperty"
    )
    def GetTimestepValues(self):
        return self._timeSteps

    # Array selection API is typical with readers in VTK
    # This is intended to allow ability for users to choose which arrays to
    # load. To expose that in ParaView, simply use the
    # smproperty.dataarrayselection().
    # This method **must** return a `vtkDataArraySelection` instance.
    @smproperty.dataarrayselection(name="2D Variables")
    def Get2DDataArrays(self):
        return self._vars2Darr

    @smproperty.dataarrayselection(name="3D Middle Layer Variables")
    def Get3DmDataArrays(self):
        return self._vars3Dmarr

    @smproperty.dataarrayselection(name="3D Interface Layer Variables")
    def Get3DiDataArrays(self):
        return self._vars3Diarr

    def RequestInformation(self, request, inInfo, outInfo):
        executive = self.GetExecutive()
        port = outInfo.GetInformationObject(0)
        port.Remove(executive.TIME_STEPS())
        port.Remove(executive.TIME_RANGE())
        if self._timeSteps is not None and len(self._timeSteps) > 0:
            for t in self._timeSteps:
                port.Append(executive.TIME_STEPS(), t)
            port.Append(executive.TIME_RANGE(), self._timeSteps[0])
            port.Append(executive.TIME_RANGE(), self._timeSteps[-1])
        return 1

    # TODO : implement request extents
    def RequestUpdateExtent(self, request, inInfo, outInfo):
        return super().RequestUpdateExtent(request, inInfo, outInfo)

    def get_time_index(self, outInfo, executive, from_port):
        timeInfo = outInfo.GetInformationObject(from_port)
        timeInd = 0
        if timeInfo.Has(executive.UPDATE_TIME_STEP()) and len(self._timeSteps) > 1:
            time = timeInfo.Get(executive.UPDATE_TIME_STEP())
            for t in self._timeSteps:
                if time <= t:
                    break
                else:
                    timeInd = timeInd + 1
            return timeInd
        return timeInd

    def RequestData(self, request, inInfo, outInfo):
        if (
            self._ConnFileName is None
            or self._ConnFileName == "None"
            or self._DataFileName is None
            or self._DataFileName == "None"
        ):
            print_error(
                "Either one or both, the data file or connectivity file, are not provided!"
            )
            return 0
        global _has_deps
        if not _has_deps:
            print_error("Required Python module 'netCDF4' or 'numpy' missing!")
            return 0

        # Getting the correct time index
        executive = self.GetExecutive()
        from_port = request.Get(executive.FROM_OUTPUT_PORT())
        timeInd = self.get_time_index(outInfo, executive, from_port)
        if self._time != timeInd:
            self._time = timeInd
            self._2d_update = True
            self._lev_update = True
            self._ilev_update = True

        meshdata = netCDF4.Dataset(self._ConnFileName, "r")
        vardata = netCDF4.Dataset(self._DataFileName, "r")

        output2D = dsa.WrapDataObject(self._output)
        dims = meshdata.dimensions
        mdims = np.array(list(meshdata.dimensions.keys()))
        mvars = np.array(list(meshdata.variables.keys()))
        ncells2D = dims[
            mdims[
                np.where(
                    (np.char.find(mdims, "grid_size") > -1)
                    | (np.char.find(mdims, "ncol") > -1)
                )[0][0]
            ]
        ].size
        if self._dirty:
            self._output = vtkUnstructuredGrid()
            output2D = dsa.WrapDataObject(self._output)

            latdim = mvars[np.where(np.char.find(mvars, "corner_lat") > -1)][0]
            londim = mvars[np.where(np.char.find(mvars, "corner_lon") > -1)][0]

            lat = meshdata[latdim][:].data.flatten()
            lon = meshdata[londim][:].data.flatten()

            coords = np.empty((len(lat), 3), dtype=np.float64)
            coords[:, 0] = lon
            coords[:, 1] = lat
            coords[:, 2] = 0.0
            _coords = dsa.numpyTovtkDataArray(coords)
            vtk_coords = vtkPoints()
            vtk_coords.SetData(_coords)
            output2D.SetPoints(vtk_coords)

            cellTypes = np.empty(ncells2D, dtype=np.uint8)
            offsets = np.arange(0, (4 * ncells2D) + 1, 4, dtype=np.int64)
            cells = np.arange(ncells2D * 4, dtype=np.int64)
            cellTypes.fill(vtkConstants.VTK_QUAD)
            cellTypes = numpy_support.numpy_to_vtk(
                num_array=cellTypes.ravel(),
                deep=True,
                array_type=vtkConstants.VTK_UNSIGNED_CHAR,
            )
            offsets = numpy_support.numpy_to_vtk(
                num_array=offsets.ravel(),
                deep=True,
                array_type=vtkConstants.VTK_ID_TYPE,
            )
            cells = numpy_support.numpy_to_vtk(
                num_array=cells.ravel(), deep=True, array_type=vtkConstants.VTK_ID_TYPE
            )
            cellArray = vtkCellArray()
            cellArray.SetData(offsets, cells)
            output2D.VTKObject.SetCells(cellTypes, cellArray)

            self._dirty = False

        # Needed to drop arrays from cached VTK Object
        to_remove = set()
        last_num_arrays = output2D.CellData.GetNumberOfArrays()
        for i in range(last_num_arrays):
            to_remove.add(output2D.CellData.GetArrayName(i))

        for varmeta in self._vars2D:
            if self._vars2Darr.ArrayIsEnabled(varmeta.name):
                if output2D.CellData.HasArray(varmeta.name):
                    to_remove.remove(varmeta.name)
                if not output2D.CellData.HasArray(varmeta.name) or self._2d_update:
                    data = vardata[varmeta.name][:].data[timeInd].flatten()
                    data = np.where(data == varmeta.fillval, np.nan, data)
                    output2D.CellData.append(data, varmeta.name)
        self._2d_update = False

        try:
            lev_field_name = "lev"
            has_lev_field = output2D.FieldData.HasArray(lev_field_name)
            lev = (
                output2D.FieldData.GetArray(lev_field_name)
                if has_lev_field
                else FindSpecialVariable(
                    vardata, EAMConstants.LEV, EAMConstants.HYAM, EAMConstants.HYBM
                )
            )
            if lev is not None:
                if not has_lev_field:
                    output2D.FieldData.append(lev, lev_field_name)
                if self._lev >= vardata.dimensions[lev_field_name].size:
                    print_error(
                        f"User provided input for middle layer {self._lev} larger than actual data {len(lev) - 1}"
                    )
                lstart = self._lev * ncells2D
                lend = lstart + ncells2D

                for varmeta in self._vars3Dm:
                    if self._vars3Dmarr.ArrayIsEnabled(varmeta.name):
                        if output2D.CellData.HasArray(varmeta.name):
                            to_remove.remove(varmeta.name)
                        if (
                            not output2D.CellData.HasArray(varmeta.name)
                            or self._lev_update
                        ):
                            if not varmeta.transpose:
                                data = (
                                    vardata[varmeta.name][:]
                                    .data[timeInd]
                                    .flatten()[lstart:lend]
                                )
                            else:
                                data = (
                                    vardata[varmeta.name][:]
                                    .data[timeInd]
                                    .transpose()
                                    .flatten()[lstart:lend]
                                )
                            data = np.where(data == varmeta.fillval, np.nan, data)
                            output2D.CellData.append(data, varmeta.name)
            self._lev_update = False
        except Exception as e:
            print_error("Error occurred while processing middle layer variables :", e)
            traceback.print_exc()

        try:
            ilev_field_name = "ilev"
            has_ilev_field = output2D.FieldData.HasArray(ilev_field_name)
            ilev = FindSpecialVariable(
                vardata, EAMConstants.ILEV, EAMConstants.HYAI, EAMConstants.HYBI
            )
            if ilev is not None:
                if not has_ilev_field:
                    output2D.FieldData.append(ilev, ilev_field_name)
                if self._ilev >= vardata.dimensions[ilev_field_name].size:
                    print_error(
                        f"User provided input for middle layer {self._ilev} larger than actual data {len(ilev) - 1}"
                    )
                ilstart = self._ilev * ncells2D
                ilend = ilstart + ncells2D
                for varmeta in self._vars3Di:
                    if self._vars3Diarr.ArrayIsEnabled(varmeta.name):
                        if output2D.CellData.HasArray(varmeta.name):
                            to_remove.remove(varmeta.name)
                        if (
                            not output2D.CellData.HasArray(varmeta.name)
                            or self._ilev_update
                        ):
                            if not varmeta.transpose:
                                data = (
                                    vardata[varmeta.name][:]
                                    .data[timeInd]
                                    .flatten()[ilstart:ilend]
                                )
                            else:
                                data = (
                                    vardata[varmeta.name][:]
                                    .data[timeInd]
                                    .transpose()
                                    .flatten()[ilstart:ilend]
                                )
                            data = np.where(data == varmeta.fillval, np.nan, data)
                            output2D.CellData.append(data, varmeta.name)
            self._ilev_update = False
        except Exception as e:
            print_error(
                "Error occurred while processing interface layer variables :", e
            )
            traceback.print_exc()

        area_var_name = "area"
        if self._areavar and not output2D.CellData.HasArray(area_var_name):
            data = vardata[self._areavar.name][:].data.flatten()
            data = np.where(data == self._areavar.fillval, np.nan, data)
            output2D.CellData.append(data, area_var_name)
        if area_var_name in to_remove:
            to_remove.remove(area_var_name)

        for var_name in to_remove:
            output2D.CellData.RemoveArray(var_name)

        output = vtkUnstructuredGrid.GetData(outInfo, 0)
        output.ShallowCopy(self._output)

        return 1
