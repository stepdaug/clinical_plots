"""
Summarising medication dates, steroid doses, CRP, temperature and clinical events against one another
@author: Stephen Auger
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import datetime
import matplotlib.dates as mdates
import matplotlib.colors as colors
import streamlit as st

title = 'Clinical data summary'
st.set_page_config(page_title=title, page_icon=(":medical_symbol:"),layout="wide",
                   menu_items={
                       'About': 'A simple tool for summarising clinical data from data in excel. If you notice any bugs or errors, or have suggestions for additional features which would be helpful then please do get in touch: stephen [dot] auger1 [at] nhs.net'
                    }
)
st.title(title)
st.write('A simple tool for helping summarise clinical data for patients who have had quite complex protracted hospital stays. Often useful for patients with ID/inflammatory issues. It plots medication dates, steroid doses/dates, lab results (e.g. CRP) and can add annotations with freetext of pertinent clinical events.')

If there’s ever a patient needing a similar summary, all it needs is the data in the attached excel file filling in, and I’d be happy to produce a plot. I’ve also attached the python code (in a .txt file) if anybody is interested in producing their own plots or making their own tweaks.
 
I’m very open to any suggestions for useful features to add or any improvements. I’m seeing if there’s a way to pull the data automatically from cerner rather needing to manually transcribe into excel, but it doesn’t look like I’ll be allowed the necessary access to the backend of cerner.

data_file = st.file_uploader("Choose a file")
if data_file is not None:
    x_interval = 2
    
     # import excel data
    meds = pd.read_excel(data_file,index_col=None,na_values=['NA'],usecols="A:C")
    crp = pd.read_excel(data_file,index_col=None,na_values=['NA'],usecols="E:F")
    steroid = pd.read_excel(data_file,index_col=None,na_values=['NA'],usecols="H:K")
    misc = pd.read_excel(data_file,index_col=None,na_values=['NA'],usecols="M:N")
    temp = pd.read_excel(data_file,index_col=None,na_values=['NA'],usecols="P:Q")
    
    # format and clean the excel data
    num_plots = 0 # how many subplots/what is there data for
    if len(meds)>0:
        num_plots=num_plots+1
        meds = meds.dropna()
        meds['Start'] = pd.to_datetime(meds['Start'], format='%d/%m/Y')
        row=0
        for end_date in meds['Finish (date or ‘ongoing’)']:
            if end_date == 'ongoing':
                meds['Finish (date or ‘ongoing’)'][row] = pd.to_datetime('today')
            row=row+1
        meds['Finish'] = pd.to_datetime(meds['Finish (date or ‘ongoing’)'])
        meds = meds.drop('Finish (date or ‘ongoing’)',axis=1)
        meds['days_start_to_end'] = meds.Finish - meds.Start
    
    if len(steroid)>0:
        num_plots=num_plots+1
        steroid = steroid.dropna()
        steroid['Start'] = pd.to_datetime(steroid['Start.1'], format='%d/%m/Y')
        row=0
        for end_date in steroid['Finish (date or ‘ongoing’).1']:
            if end_date == 'ongoing':
                steroid['Finish (date or ‘ongoing’).1'][row] = pd.to_datetime('today', format='%d/%m/Y')
            row=row+1
        steroid['Finish'] = pd.to_datetime(steroid['Finish (date or ‘ongoing’).1'], format='%d/%m/Y')
        steroid['days_start_to_end'] = steroid.Finish - steroid.Start
        steroid = steroid.drop(['Start.1','Finish (date or ‘ongoing’).1'], axis=1)
    
    if len(crp)>0 or len(misc)>0 or len(temp)>0:
        num_plots=num_plots+1
        crp = crp.dropna()
        crp['Date'] = pd.to_datetime(crp['Date'], format='%d/%m/Y')
        misc = misc.dropna()
        misc['Date'] = pd.to_datetime(misc['Date.1'], format='%d/%m/Y')
        misc = misc.drop('Date.1',axis=1)
        temp = temp.dropna()
        temp['Date'] = pd.to_datetime(temp['Date.2'], format='%d/%m/Y')
        temp = temp.drop('Date.2',axis=1)
        temp = temp.sort_values(by='Date').reset_index()
    
    # start and end of plotting period
    first_date = min([min(meds.Start),min(crp.Date),min(steroid.Start),min(misc.Date),min(temp.Date)])
    last_date = max([max(meds.Finish),max(crp.Date),max(steroid.Finish),max(misc.Date),max(temp.Date)])
    
    fig, ax = plt.subplots(num_plots,figsize=(25,10*num_plots))
    ax_num=0
    # plot CRP and clinical events text
    if len(crp)>0:
        crp_plot = ax[ax_num].plot(crp.Date,crp.CRP,'ro-',label='CRP')
        ax[ax_num].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))  # display ticks as hours and minutes
        ax[ax_num].xaxis.set_major_locator(mdates.DayLocator(interval=1))  # set a tick every hour
        ax[ax_num].set_xlim(first_date,last_date)
        ax[ax_num].tick_params(axis='both', which='major',length=5,width=2,labelsize=20)
        ax[ax_num].grid(which='major', axis='x', linestyle='--')
        for label in ax[ax_num].get_xticklabels():
            label.set_ha("center")
            label.set_rotation(90)
        ax[ax_num].set_ylabel('CRP (mg/L)',fontsize=25,weight='bold')
       
        misc = misc.sort_values(by='Date').reset_index()
        row = 0
        for event in misc.Note:
            if (row % 5) == 0 or row == 0: # alternate height values
                height = 100
            elif ((row+4) % 5) == 0:
                height = 80
            elif ((row+3) % 5) == 0:
                height = 60
            elif ((row+2) % 5) == 0:
                height = 40
            elif ((row+1) % 5) == 0:
                height = 20
            ax[ax_num].annotate(event,(misc.Date[row],max(crp.CRP)),(misc.Date[row],max(crp.CRP)+height), ha="center", va="center", arrowprops = {"arrowstyle": "->", "color": "C1"},fontsize=20,weight='light')
            row=row+1
        ax_num=ax_num+1
     
    # plot temperature on a secondary axis in the same subplot as CRP
    if len(temp)>0:
        if ax_num == 1:
            ax2 = ax[ax_num-1].twinx()
        temp_plot = ax2.plot(temp.Date,temp.Temperature,'bo-',label='Temperature')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))  # display ticks as hours and minutes
        ax2.xaxis.set_major_locator(mdates.DayLocator(interval=x_interval))  # set a tick every hour
        ax2.set_xlim(first_date,last_date)
        ax2.set_ylim(min(temp.Temperature),max(temp.Temperature))
        ax2.tick_params(axis='y', which='major',length=5,width=2,labelsize=20)
        ax2.set_ylabel('Peak daily temperature (celcius)',fontsize=25,weight='bold')
        ax_num = 1
     
    lns = crp_plot + temp_plot
    labs = [l.get_label() for l in lns]
    ax[ax_num-1].legend(lns,labs,loc='upper right', fontsize=25)
     
    # plot medication dates
    if len(meds)>0:
        ax[ax_num].barh(meds.Medication, meds.days_start_to_end, left=meds.Start)
        ax[ax_num].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))  # display ticks as hours and minutes
        ax[ax_num].xaxis.set_major_locator(mdates.DayLocator(interval=x_interval))  # set a tick every hour
        ax[ax_num].set_xlim(first_date,last_date)
        ax[ax_num].tick_params(axis='both', which='major',length=5,width=2,labelsize=20)
        ax[ax_num].tick_params(axis='y', which='major',length=5,width=2,labelsize=25)
        ax[ax_num].invert_yaxis()
        for label in ax[ax_num].get_xticklabels():
            label.set_ha("center")
            label.set_rotation(90)
        ax[ax_num].grid(which='major', axis='x', linestyle='--')
        ax_num=ax_num+1
     
    # plot steroid dates and doses
    if len(steroid)>0:
        barlist=ax[ax_num].barh(steroid.Steroid, steroid.days_start_to_end, left=steroid.Start)
        # set the bar colour according to steroid dose
        for bar in range(0,len(barlist)):
            if steroid.Steroid[bar] == 'Prednisolone':
                pred_equiv_dose = steroid.Daily_dose[bar]
            elif steroid.Steroid[bar] == 'Methylprednisolone':
                pred_equiv_dose = steroid.Daily_dose[bar] / 0.8
            elif steroid.Steroid[bar] == 'Dexamethasone':
                pred_equiv_dose = steroid.Daily_dose[bar] / 0.15
            elif steroid.Steroid[bar] == 'Hydrocortisone':
                pred_equiv_dose = steroid.Daily_dose[bar] / 4
            barlist[bar].set_color(cm.coolwarm(pred_equiv_dose/60))
            barlist[bar].set_alpha(1)
        # add colourbar at bottom of the plot
        cbar = fig.colorbar(cm.ScalarMappable(cmap=cm.coolwarm), ax=ax[ax_num],location='bottom',aspect=50,fraction=0.05,pad=0.2)
        cbar.set_label(label='Daily equivalent prednisolone dose (mg)',fontsize=25,weight='bold')
        cbar.set_ticks([0, 1/6, 2/6, 3/6, 4/6, 5/6, 1])
        cbar.set_ticklabels(['0','10','20','30','40','50','60+'],fontsize=20)
        # text inside the bars indicating the dose
        for bar, ster_dose in zip(ax[ax_num].patches,steroid.Daily_dose[:]):
            ax[ax_num].text(bar.get_x()+bar.get_width()/2, bar.get_y()+bar.get_height()/2,str(round(ster_dose)) + 'mg', color = 'white', ha = 'center', va = 'center', fontsize=20, weight='bold')
        # format axes
        ax[ax_num].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))  # display ticks as hours and minutes
        ax[ax_num].xaxis.set_major_locator(mdates.DayLocator(interval=x_interval))  # set a tick every hour
        ax[ax_num].set_xlim(first_date,last_date)
        ax[ax_num].tick_params(axis='both', which='major',length=5,width=2,labelsize=20)
        ax[ax_num].tick_params(axis='y', which='major',length=5,width=2,labelsize=25)
        ax[ax_num].invert_yaxis()
        for label in ax[ax_num].get_xticklabels():
            label.set_ha("center")
            label.set_rotation(90)
        ax[ax_num].grid(which='major', axis='x', linestyle='--')
        ax_num=ax_num+1
        
    st.pyplot(fig)