# #   Despy: A discrete event simulation framework for Python
# #   Version 0.1
# #   Released under the MIT License (MIT)
# #   Copyright (c) 2015, Stacy Irwin
# """
# **********************
# despy.output.generator
# **********************
# 
# ..  autosummary::
# 
#     Generator
#     
# ..  todo::
# 
#     Make _full_path attribute a documented public attribute.
#     
#     Put statistic csv stuff in correct place, fix component traversal.
# """
# import os
# import csv
# 
# import numpy as np
# 
# from despy.core.component import Component
# from despy.output.trace import Trace
# from despy.output.report import HtmlReport
#     
# class Generator(object):
#     """Generates the simulation's output reports and graphs.
#     
#     **Members**
#     
#     ..  autosummary
#     
#         console_trace
#         folder_basename
#         sim
#         write_files
#         set_full_path
#             
#     **Python Library Dependencies**
#         * :mod:`os`
#     
#     """
#     
#             
#     def __init__(self, config):
#         """Construct a Generator object.
#         
#         *Arguments*
#             ``simulation`` :class:`despy.core.simulation.Simulation`
#                 Corresponding simulation object.
#         """
#         self._config = config
#         
#     def write_files(self):
#         """Creates trace and HTML reports in folder_basename location.
#         """
#         
#         # Take no action if no output folder specified.
#         if self._config.folder_basename is None:
#             return None
#         
#         # Finalize model and components.
#         
#         # Write trace csv file.
#         self.set_full_path()
#         self._config.trace.write_csv(self._full_path)
#         
#         #Get data for all components and create HTML report.
#         self._config.report.append_output(self.sim.get_data())
#             
#         for _, component in self.sim.model.components.items():
#             output = component.get_data()
#             if output is not None:
#                 self._config.report.append_output(output)
#         
#         self._config.report.write_report(self._full_path)
#         
#         #DEBUG:
# #         print()
# #         print("=====COMPONENT LIST=====")
# #         for cpt in Component.register:
# #             print("Component: {}".format(cpt.name))
# #         print()
#         
#         #Write CSV file for each statistic        
# #         for cpt in self.sim.model:
# #             for _, st in cpt.statistics.items():
# #                 f_name = cpt.slug + '-' + st.name + '.csv'
# #                 f_pname = self._full_path + '/' + f_name
# #                 print("Name: {}, Index List{}".format(st.name, st._index)) #DEBUG:
# #                 with open(f_pname, 'w', newline = '') as file:
# #                     writer = csv.writer(file)
# #                     writer.writerow(["Statistic: {}".format(f_name)])
# #                     writer.writerow([])
# #                     writer.writerow(["Max Rep Length",
# #                                      st.max_rep_length])
# #                     writer.writerow([])
# #                     writer.writerow(["Rep-{}".format(i)
# #                                      for i in range(st.reps)])
# #                     vals = [st.rep_lengths]
# # #                     vals = ([[st.get_val(r, i)
# # #                                 for i in range(st.rep_lengths[r])]
# # #                                 for r in range(st.reps)])
# #                     print()
# #                     print("!!!!!!{}!!!!!!".format(st.name))
# #                     print("Num Reps: {}".format(st.reps))
# #                     print("=====Flat Values=====")
# #                     print(st.values)
# #                     print("=====Rep Lengths")
# #                     print(st.rep_lengths)
# #                     print("======Original Matrix======")
# #                     print(vals) #DEBUG:
# #                     print("=====Transposed Matrix======")
# #                     t_vals = np.transpose(vals)
# #                     print(t_vals) #DEBUG:
# #                     writer.writerows(t_vals)
#                         
#         
#     def set_full_path(self):
#         """Adds time-stamp to end of Generator.folder_basename.
#         
#         The time-stamp is the stop time for the simulation.
#         """
#         timestamp = \
#                 self._sim.run_stop_time.strftime('_%y_%j_%H_%M_%S')
#         self._full_path = self.folder_basename + '/Run' + timestamp
#                 
#         if not os.path.exists(self._full_path):
#             os.makedirs(self._full_path)             
#         

