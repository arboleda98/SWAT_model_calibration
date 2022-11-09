#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import importlib as ipl

import os
from pathlib import Path
import uuid
import shutil
import sys
import traceback

import numpy as np
import pandas as pd

import SimManage
import File_Edit
import ReadOut

from File_Edit import fileCioManipulator, bsnManipulator, gwManipulator, solManipulator
from File_Edit import hruManipulator, rteManipulator, mgtManipulator, subManipulator
import hydroeval
import spotpy
import MySQLdb
import datetime
import scipy
from scipy import signal
""" from Consulta_BD_Cadatos_VE1 import *  function to extract series of level or flow from database, in case of not requiring query, 
modify the function in such a way that an array with the observed flows is given to the function. """


# In[ ]:


def calibracion_swat (estacion, fecha_ini_calib, fecha_fin_calib, coeficiente_a_curva, coeficiente_b_curva, DT,
nombre_carpeta_modelacion, rep, version_swat, fobj, calibracion_definitiva = True):

     """
    IMPORTANT: 
    BEFORE EXECUTING THE FUNCTION IT IS IMPORTANT TO VERIFY THAT THE LEVEL SERIES IS OF GOOD QUALITY.
    BEFORE EXECUTING THE FUNCTION IT IS IMPORTANT THAT THE CALLED .py FILES ARE IN THE SAME FOLDER:
    1. File_Edit.py
    2. ReadOut.py
    3. SimManage.py
    4. Consulta_BD_Cadatos_VE1

    - In the modeling folder create a new folder named: params,
    in this folder create the file with the parameters definition.

    - In the TxtInOut folder there must be an executable of the SWAT model for Linux or Windows with the necessary permissions
    permissions

    To use the function, the following variables are received

    station: level station code, e.g.: 236, 101, 238, 99, 93
    date_ini_calib: initial date of the modeling in format 'YYYYY-MM-DD HH:MM:SS'.
    end_calib_date: end date of modeling in format 'YYYYY-MM-DD HH:MM:SS'.
    coefficient_a_curve: coefficient a of the curve of the level station (Q=a*N^b, where N is the level)
    coefficient_b_curve: coefficient b of the curve of the level station (Q=a*N^b, where N is the level)
    DT: time step of the modeling to be calibrated IN MINUTES, if every 15 minutes DT=15, if every hour DT=60
    modeling_folder_name: put only the name of the folder, if the folder is called '101_15min', put 101_15min...
    rep: number of iterations to be made during calibration
    version_swat: SWAT executable to be used in the calibration, currently the following versions of the executable are available,
    NOTE: not all versions are suitable for all basins.
        swat670_static.exe, version_swat = 1,
        SWAT_Rev622, version_swat = 2,
        SWAT_Rev681, version_swat = 3,
        SWAT_Rev670_2, version_swat = 4.
    fobj: objective function can be:
    1 = 'NSE' or 2 ='KGE'.
    """
    os.chdir('/var/datos_hidrologia/CarlosA/copias_swat2/'+str(nombre_carpeta_modelacion)+'/') ##Path where the modeling is stored
    ###=================###
    ###CONSULTA DE NIVEL###
    ###=================###
    Prueba = seguimiento(estacion 
                        ,fecha_ini_calib[0:10] 
                        ,fecha_fin_calib[0:10]
                        ,fecha_ini_calib[11:19]
                        ,fecha_fin_calib[11:19]
                        ,calidad='Si')

    df_nivel = (Prueba.data())
    del df_nivel['fecha_hora']
    df_nivel=df_nivel/100
    df_nivel = df_nivel.resample(str(DT)+'min').mean()

    df_nivel['flow'] = coeficiente_a_curva*df_nivel['nivel']**coeficiente_b_curva
    df_nivel['flow'] = df_nivel['flow'].replace(['""'], np.NAN)
    c= (df_nivel.flow.values)
    flow = pd.DataFrame(c)

    array_flow = np.savetxt('./TxtInOut/discharge.txt',flow.values.ravel()) 
    ###================###
    ###SPOT CALIBRATION###
    ###================###

    class swat_callib_setup(object):

        def __init__(self, swat_model, observed_data, param_defs, parallel="seq", temp_dir=None):

            self.model = swat_model
            self.observed_data = observed_data
            
            self.params = []
            for i in range(len(param_defs)):
                self.params.append(
                    spotpy.parameter.Uniform(
                        name=par_file_load[i][0],
                        low=par_file_load[i][1],
                        high=par_file_load[i][2],
                        optguess=np.mean( [par_file_load[i][1], par_file_load[i][2]] )))
        
            self.temp_dir = temp_dir
            self.parallel = parallel

            if self.parallel == "seq":
                pass

            if self.parallel == "mpi":

                from mpi4py import MPI

                comm = MPI.COMM_WORLD
                self.mpi_size = comm.Get_size()
                self.mpi_rank = comm.Get_rank()
        

        def onerror(self, func, path, exc_info):
            import stat
            if not os.access(path, os.W_OK):
                # Is the error an access error ?
                os.chmod(path, stat.S_IWUSR)
                func(path)
            else:
                raise


        def prep_temp_model_dir(self):
            temp_id = uuid.uuid1()

            if self.parallel == "mpi":
                try:
                    temp_id = f'mpi{self.mpi_rank}_' + str(temp_id)
                except NameError:
                    pass

            test_path = f"swat_{temp_id}"

            if self.temp_dir is None:
                test_path = Path(os.path.join(os.getcwd(), test_path))
            else:
                test_path = Path(os.path.join(self.temp_dir, test_path))

            if os.path.exists(test_path):
                print('Deleting temp folder ' + str(test_path))
                shutil.rmtree(test_path, onerror=self.onerror)

            print('Copying model to folder ' + str(test_path))
            shutil.copytree(self.model.working_dir, test_path)

            try:
                return SimManage.SwatModel.loadModelFromDirectory(test_path)
            except ValueError:
                return SimManage.SwatModel.initFromTxtInOut(test_path, copy=False, force=True)
        

        def remove_temp_model_dir(self, model):
            try:
                print('Deleting temp folder ' + str(model.working_dir))
                shutil.rmtree(model.working_dir, onerror=self.onerror)
            except Exception as e:
                print(e)
                traceback.print_exc(file=sys.stdout)
                print('Error deleting tmp model run')
                pass
        

        def manipulate_model_params(self, model, parameters):

            print(f"this iteration's parameters:")
            print(parameters)
            print(self.params[0].name)
        # print(parameters['v__SFTMP.bsn'])
            
            how_apply = {
                'v':'s',
                'r':'*',
                'a':'+'
            }
            
            for idx, param_string in enumerate(self.params):
                print(param_string.name)
                print(idx)
                print(len(param_string.name))
                print(parameters[idx])
                
                # slice the stringname open
                # how  param  manipu   1        2         3          4         5   (times __)
                # x__<parname>.<ext>__<hydrp>__<soltext>__<landuse>__<subbsn>__<slope>
                # [0] split ('.')  split ('__') [0]  how v_s r_* a_+  [1] param field name
                # ---
                # [1] split('__') [0] manipulator/file type [1] hydgrp ... etc
                
            # left, right = param_string.name.split('.')
            # how, param_field = left.split('__')
                
            # right_list = right.split('__')
            # manip_ext = right_list[0]
            # if len(right_list) > 1:
            #     hydrp = right_list[1]
            # if len(right_list) > 2:
            #     soltext = right_list[2]
            # if len(right_list) > 3:
            #     landuse = right_list[3]
            # if len(right_list) > 4:
            #     subbsn = right_list[4]
            # if len(right_list) > 5:
            #     slope = right_list[5]
                how = param_string.name.split('__')[0]
                right = param_string.name.split('.')
                param_field = [param_string.minbound, param_string.maxbound]
                right_list=right[0].split('__')
                name_1 = right[0].split('__')[1]
                manip_ext = right_list[2]

                if len(right_list) > 1:
                    hydrp = right_list[1]
                if len(right_list) > 2:
                    soltext = right_list[2]
                if len(right_list) > 3:
                    landuse = right_list[3]
                if len(right_list) > 4:
                    subbsn = right_list[4]
                if len(right_list) > 5:
                    slope = right_list[5]

                changeHow = how_apply[how]

                
                print(f"field {param_field} in file/manip {manip_ext} will be changed via '{changeHow}' and value {parameters[idx]} ")
                
                manipulator_handle = model.getFileManipulators()[manip_ext]
                
                for m in manipulator_handle:
                # m.setChangePar(param_field, parameters[idx], changeHow)
                    m.setChangePar(name_1, parameters[idx], changeHow)
                    m.finishChangePar()
                    

        def parameters(self):
            return spotpy.parameter.generate(self.params)
        
        
        def evaluation(self):
            # observations = [self.observed_data]
            return self.observed_data


        def simulation(self, parameters):
            the_model = self.prep_temp_model_dir()
            the_model.enrichModelMeta(verbose=False)
            print(f"is it runnable: {the_model.is_runnable()}")

            self.manipulate_model_params(the_model, parameters)

            # TODO: edit the correct parameters in SWAT files

            ret_val = the_model.run(capture_logs=False, silent=False)
            print(f"returns {ret_val} - vs {the_model.last_run_succesful}")
            # print(model4.last_run_logs)

            reach = 1
            # simulated data
            with open (str(the_model.working_dir)+'/watout_hr.dat') as file:
                lineas = file.readlines()
            primera_fila = lineas[5:6][0].replace(' ',',').replace(',,',',').replace(',,,',',').replace(',,',',').replace('\n','')
            lista_contenido =[]
            for i in range(len(lineas[6:len(lineas)])):

                segunda_linea=lineas[6:len(lineas)][i].replace(' ',',').replace(',,',',').replace(',,,',',').replace(',,',',').replace('\n','')
                lista_contenido.append(segunda_linea)
                #print(i)
            lista_primera_fila = primera_fila.split(',')
            ensayo=pd.DataFrame(columns=[lista_primera_fila[0:5]])
            listica = []
            for i in range(0,len(lista_contenido)):
                listica.append(lista_contenido[i].split(','))

            df = pd.DataFrame(listica)
            simulated_values=df[4].values.astype(float)

            self.remove_temp_model_dir(the_model)
            return simulated_values

        if fobj == 1:

            def objectivefunction(self, simulation, evaluation):
                print("simulation")
                print(len(simulation))
                print("evaluation")
                print(len(evaluation))
                objectivefunction = spotpy.objectivefunctions.nashsutcliffe(evaluation,simulation)
                return objectivefunction

        if fobj == 2:

             def objectivefunction(self, simulation, evaluation):
                print("simulation")
                print(len(simulation))
                print("evaluation")
                print(len(evaluation))
                df1 = pd.DataFrame(list(zip(simulation, evaluation))).dropna()
                objectivefunction = np.round(hydroeval.kge(df1[0].values,df1[1].values)[0][0],3)
                #objectivefunction = spotpy.objectivefunctions.kge(evaluation,simulation)
                return objectivefunction

    model4 = {}

    try:
        model4 = SimManage.SwatModel.initFromTxtInOut(txtInOut=os.path.join('./',os.path.join('TxtInOut')), copy=True, target_dir="/var/datos_hidrologia/CarlosA/copias_swat/"+str(nombre_carpeta_modelacion)+"/", force=False, version_swat=version_swat) ##path where the modeling will be stored
    except ValueError:
        model4 = SimManage.SwatModel.loadModelFromDirectory("/var/datos_hidrologia/CarlosA/copias_swat/"+str(nombre_carpeta_modelacion)+"/", version_swat=version_swat)

    model4.enrichModelMeta()
    print(f"is it runnable: {model4.is_runnable()}")

    #temp_dir = 'swat_b7c411b6-d727-11ea-b9a4-54e1ad562245'
    os.chdir("/var/datos_hidrologia/CarlosA/copias_swat/"+str(nombre_carpeta_modelacion)+"/")

    with open ('./watout_hr.dat') as file:
        lineas = file.readlines()
    primera_fila = lineas[5:6][0].replace(' ',',').replace(',,',',').replace(',,,',',').replace(',,',',').replace('\n','')
    lista_contenido =[]
    for i in range(len(lineas[6:len(lineas)])):
        
        segunda_linea=lineas[6:len(lineas)][i].replace(' ',',').replace(',,',',').replace(',,,',',').replace(',,',',').replace('\n','')
        lista_contenido.append(segunda_linea)
        #print(i)
    lista_primera_fila = primera_fila.split(',')
    ensayo=pd.DataFrame(columns=[lista_primera_fila[0:5]])
    listica = []
    for i in range(0,len(lista_contenido)):
        listica.append(lista_contenido[i].split(','))
        
    df = pd.DataFrame(listica)
    simulated_values=df[4].values.astype(float)

    observed_values = np.loadtxt('./discharge.txt')
    df1= pd.DataFrame(list(zip(simulated_values,observed_values)))
    df1=df1.rename(columns={0:'caudal_sim', 1:'caudal_obs'})

    if fobj == 1:


        nse_pen= np.round(hydroeval.nse(df1.dropna().caudal_sim.values,df1.dropna().caudal_obs.values),3)

        print(f"initial NSE: {nse_pen}")
    
    elif fobj == 2:

        kge_pen= np.round(hydroeval.kge(df1.dropna().caudal_sim.values,df1.dropna().caudal_obs.values)[0][0],3)
        
        print(f"initial KGE: {kge_pen}")

    temp_dir = '/var/datos_hidrologia/CarlosA/copias_swat/'+str(nombre_carpeta_modelacion)+'/'

    par_file_name = os.path.join('./', os.path.join('params','par_inf.txt'))
    print(f'loading parameter file {par_file_name}')


    dtype=[('f0', '|U30'), ('f1', '<f8'), ('f2', '<f8')]
    par_file_load = np.genfromtxt(par_file_name, dtype=dtype, encoding='utf-8')

    parallel = "seq"
    spot_setup=swat_callib_setup(model4, observed_values, par_file_load, parallel=parallel, temp_dir=temp_dir)
    repetitions=rep

    dbformat = "csv"

    lhs_calibrator_sampler = spotpy.algorithms.lhs(spot_setup, parallel=parallel, dbname='./copiasDemo4SwatLHS', dbformat=dbformat)
    #lhs_calibrator_sampler = spotpy.algorithms.sceua(spot_setup, parallel=parallel, dbname='Deo4SwatLHS', dbformat=dbformat)

    lhs_calibrator_sampler.sample(repetitions)

    callib_results = lhs_calibrator_sampler.getdata()



    red = pd.read_csv('./copiasDemo4SwatLHS.csv')

    best_sim=red.loc[red.loc[:, 'like1'] == float(np.max(red.like1))]
   
    fun_obj_maxima = float(np.max(red.like1))


    best_sim = best_sim.rename(columns={'like1':'NSE'})

    df_params = pd.DataFrame((best_sim.iloc[0][1:len(par_file_load)+1]))

    df_params = df_params.reset_index()
    df_params_1 = df_params[df_params.columns[0]] = df_params[df_params.columns[0]].str.replace("par", "")
    
    df_params = df_params.set_index('index')
    df_params.to_csv('./new_pars.txt', header=False, index=True, sep=' ')


    ####=======================####
    ####REPLACE NEW PARAMETERS####
    ####=======================####
    par_file_name = os.path.join('./', os.path.join('new_pars.txt'))


    dtype=[('f0', '|U30'), ('f1', '<f8')]
    par_file_load = np.genfromtxt(par_file_name, dtype=dtype, encoding='utf-8')

    params = []
    for i in range(len(par_file_load)):
        params.append(
            spotpy.parameter.Uniform(
                name=par_file_load[i][0],
                low=par_file_load[i][1],
                high = par_file_load[i][1],
                optguess=np.mean( [par_file_load[i][1], par_file_load[i][1]] )))

    def manipulate_model_params(model, parameters):

        
        how_apply = {
            'v':'s',
            'r':'*',
            'a':'+'
        }
        
        for idx, param_string in enumerate(params):
            print(param_string.name)
            print(idx)
            print(len(param_string.name))
            print(parameters[idx])

            how = param_string.name.split('__')[0]
            right = param_string.name.split('.')
            #param_field = [param_string.minbound, param_string.maxbound]
            right_list=right[0].split('__')
            name_1 = right[0].split('__')[1]
            manip_ext = right_list[2]

            if len(right_list) > 1:
                hydrp = right_list[1]
            if len(right_list) > 2:
                soltext = right_list[2]
            if len(right_list) > 3:
                landuse = right_list[3]
            if len(right_list) > 4:
                subbsn = right_list[4]
            if len(right_list) > 5:
                slope = right_list[5]

            changeHow = how_apply[how]

            
            
            manipulator_handle = model4.getFileManipulators()[manip_ext]
            
            for m in manipulator_handle:
               # m.setChangePar(param_field, parameters[idx], changeHow)
                m.setChangePar(name_1, par_file_load[idx][1].mean(), changeHow)
                m.finishChangePar()

        
    manipulate_model_params(model4, params)
   
    ret_val = model4.run(capture_logs=False, silent=False)
    
    if calibracion_definitiva == False:
        shutil.rmtree('/var/datos_hidrologia/CarlosA/copias_swat/'+str(nombre_carpeta_modelacion))

    else:
        pass

    return (df_params,fun_obj_maxima )

