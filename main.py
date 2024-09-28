import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
import matplotlib.pyplot as plt
import re
# Global variables
global ppsm, stsm, stim, ppss, stss, stis, ppsu, stsu, stiu
global perm, pers, peru, stes, steu, stem
global t, tpi, tf, nsm, nss, nsu, nt, HV
global itom, itos, itou
global stom, stos, stou
global ptom, ptos, ptou
# Initialize global variables
ppsm = stsm = stim = ppss = stss = stis = ppsu = stsu = stiu = 0
perm = pers = peru = stes = steu = stem = 0
stom = stos = stou = 0
ptom = ptos = ptou = 0
t = tpi = 0
tf = 100  # mins
nsm = nss = nsu = nt = 0
HV = float('inf')

def is_time_format(s):
    if not isinstance(s, str):
        return False
    if len(s) != 5:
        return False
    if s[2] != ':':
        return False
    hours, minutes = s.split(':')
    if not (hours.isdigit() and minutes.isdigit()):
        return False
    if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
        return False
    return True

def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df = df.drop(['multiple_deliveries', 'Vehicle_condition', 'Type_of_order', 'Delivery_location_longitude',
                  'Festival', 'Road_traffic_density', 'Delivery_person_Ratings', 'Restaurant_latitude', 'Restaurant_longitude',
                  'Weather_conditions', 'Delivery_location_latitude', 'Delivery_person_Age', 'ID', 'Type_of_vehicle'], axis=1)
    
    # Strip whitespace and filter rows where Time_Orderd is in a valid time format
    df['Time_Orderd'] = df['Time_Orderd'].astype(str).str.strip()
    df = df[df['Time_Orderd'].apply(is_time_format)].copy()
    
    # Convert Time_Orderd to datetime.time
    df['Time_Orderd'] = pd.to_datetime(df['Time_Orderd'], format='%H:%M').dt.time
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

    df['DateTime'] = df.apply(lambda row: datetime.combine(row['Order_Date'], row['Time_Orderd']), axis=1)
    df = df.sort_values('DateTime')
    df['Time_Between_Orders'] = df['DateTime'].diff().dt.total_seconds() / 60
    df = df.dropna(subset=['Time_Between_Orders'])
    df['Day_of_Week'] = df['Order_Date'].dt.day_name()

    return df

def calculate_kde(df):
    weekend_days = ['Friday', 'Saturday', 'Sunday']
    weekend_df = df[df['Day_of_Week'].isin(weekend_days)]
    weekday_df = df[~df['Day_of_Week'].isin(weekend_days)]

    ip_semana = stats.gaussian_kde(weekday_df['Time_Between_Orders'])
    ip_finde = stats.gaussian_kde(weekend_df['Time_Between_Orders'])
    te_semana = stats.gaussian_kde(weekday_df['Time_taken (min)'])
    te_finde = stats.gaussian_kde(weekend_df['Time_taken (min)'])


    return ip_semana, ip_finde, te_semana, te_finde

def input_valid_day():
    days_of_week = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    while True:
        day = input("Introduce un día de la semana: ").strip().lower()
        if day in days_of_week:
            return day
        print("Entrada no válida. Por favor, introduce un día de la semana válido.")

def time_for_fdp(kde):
    x_range = np.linspace(0, 60, 2000)
    density_values = kde(x_range)
    density_values /= np.sum(density_values)
    return np.random.choice(x_range, p=density_values)

def delivery_time_for_day(day, te_semana, te_finde):
    weekend_days = ["viernes", "sabado", "domingo"]
    return time_for_fdp(te_finde if day in weekend_days else te_semana)

def arrival_time_for_day(day, ip_semana, ip_finde):
    weekend_days = ["viernes", "sabado", "domingo"]
    return time_for_fdp(ip_finde if day in weekend_days else ip_semana)

def input_delivery_personnel(zone):
    return int(input(f"Ingrese la cantidad de repartidores de la zona {zone}: "))

def deliver_order(tpe, i, sts, ste, ns, delivery_personnel, day, ito, te_semana, te_finde):
    global t
    t = tpe[i]
    sts += t
    ns -= 1
    if ns >= delivery_personnel:
        te = delivery_time_for_day(day, te_semana, te_finde)
        tpe[i] = t + te
        ste += te
    else:
        tpe[i] = HV
        ito[i] = t

    return (sts, ste)

def arrival_time(day, ip_semana, ip_finde):
    r1, r2 = np.random.random(2)
    if r1 <= 0.768:
        return delivery_time_for_day(day, ip_semana, ip_finde)
    elif r1 <= 0.996:
        return delivery_time_for_day(day, ip_semana, ip_finde)
    else:
        return delivery_time_for_day(day, ip_semana, ip_finde)

def buscar_repartidor_libre(tpe):
    return np.argmax(tpe)

def order_arrival(ip_semana, ip_finde, day, ns, delivery_personnel, ito, te_finde, te_semana, tpe, sto, sti, ste):
    global tpi, t, nt
    ip = arrival_time(day, ip_semana, ip_finde)
    tpi = t + ip
    ns += 1
    nt += 1
    sti += t
    if ns <= delivery_personnel:
        i = buscar_repartidor_libre(tpe)
        te = delivery_time_for_day(day, te_semana, te_finde)
        tpe[i] = t + te
        ste += te
        sto += t - ito[i]

    return (sti, ste, sto)

def process_order(r1):
    global nsm, nsu, nss
    

def simulation(ip_semana, ip_finde, te_semana, te_finde):
    global t, tpi, nsm, nss, nsu, stim, stiu, stis, stem, steu, stes, stou, stos, stom, stsm, stss, stsu
    m = input_delivery_personnel("Metropolitana")
    u = input_delivery_personnel("Urbana")
    s = input_delivery_personnel("Semi-Urbana")
    day = input_valid_day()

    tpem = np.full(m, HV)
    tpes = np.full(s, HV)
    tpeu = np.full(u, HV)
    itom = np.full(m, t)
    itos = np.full(s, t)
    itou = np.full(u, t)
    

    while t < tf:
        x = np.argmin(tpes)
        i = np.argmin(tpem)
        j = np.argmin(tpeu)

        next_event = min(tpeu[j], tpem[i], tpes[x], tpi)
        
        if next_event == tpi:
            t = tpi
            r = np.random.random()
            if r <= 0.768:
                stim , stem, stom = order_arrival(ip_semana, ip_finde, day, nsm, m, itom, te_finde, te_semana, tpem, stom, stim, stem)
            elif r <= 0.996:
                stiu , steu, stou = order_arrival(ip_semana, ip_finde, day, nsu, u, itou, te_finde, te_semana, tpeu, stou, stiu, steu)
            else:
                stis , stes, stos = order_arrival(ip_semana, ip_finde, day, nss, s, itos, te_finde, te_semana, tpes, stos, stis, stes)
        elif next_event == tpem[i]:
            stsm, stem = deliver_order(tpem, i, stsm, stem, nsm, m, day, itom, te_semana, te_finde)
        elif next_event == tpes[x]:
            stss, stes = deliver_order(tpes, x, stss, stes, nss, s, day, itos, te_semana, te_finde)
        elif next_event == tpeu[j]:
            stsu, steu = deliver_order(tpeu, j, stsu, steu, nsu, u, day, itou, te_semana, te_finde)

    while (nsm > 0 or nsu > 0 or nss > 0):
        x = np.argmin(tpes)
        i = np.argmin(tpem)
        j = np.argmin(tpeu)

        next_event = min(tpeu[j], tpem[i], tpes[x])
        
        if next_event == tpem[i]:
            stsm, stem = deliver_order(tpem, i, stsm, stem, nsm, m, day, itom, te_semana, te_finde)
        elif next_event == tpes[x]:
            stss, stes = deliver_order(tpes, x, stss, stes, nss, s, day, itos, te_semana, te_finde)
        elif next_event == tpeu[j]:
            stsu, steu = deliver_order(tpeu, j, stsu, steu, nsu, u, day, itou, te_semana, te_finde)
    
    if stos == 0:
        stos = t


def calcular_y_mostrar_resultados():
    global stom, stos, stou, t
    global stsm, stim, stss, stis, stiu, stsu, nt
    global stem, stes, steu

    print(f"Porcentaje de tiempo ocioso de repartidores en la zona metropolitana: {(stom / t) * 100} minutos")
    print(f"Porcentaje de tiempo ocioso de repartidores en la zona semi-urbana: {(stos / t) * 100 } minutos")
    print(f"Porcentaje de tiempo ocioso de repartidores en la zona urbana: {(stou / t) * 100} minutos")

    print(f"Promedio de permanencia en sistema en la zona metropolitana: {(stsm - stim) / nt} minutos")
    print(f"Promedio de permanencia en sistema en la zona semi-urbana: {(stss - stis) / nt} minutos")
    print(f"Promedio de permanencia en sistema en la zona urbana: {(stsu - stiu) / nt} minutos")

    print(f"Promedio de espera hasta que un pedido es atendido por un repartidor en la zona metropolitana: {(stsm - stim - stem) / nt} minutos")
    print(f"Promedio de espera hasta que un pedido es atendido por un repartidor en la zona semi-urbana: {(stss - stis - stes) / nt} minutos")
    print(f"Promedio de espera hasta que un pedido es atendido por un repartidor en la zona urbana: {(stsu - stiu - steu) / nt} minutos")

if __name__ == "__main__":
    df = load_and_preprocess_data('zomato-dataset.csv')
    ip_semana, ip_finde, te_semana, te_finde = calculate_kde(df)
    simulation(ip_semana, ip_finde, te_semana, te_finde)
    calcular_y_mostrar_resultados()
