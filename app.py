from flask import Flask, jsonify, make_response
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

most_recent_date = session.query(func.max(Measurement.date)).all()[0][0]
date_one_year_prev_most_recent = (dt.datetime(2017, 8, 23) - dt.timedelta(days=365)).strftime('%Y-%m-%d')

app = Flask(__name__)

@app.route('/')
def home():
    routes = ['milk', 'man', 'stam']
    return routes[0]

@app.route('/api/v1.0/precipitation')
def prcp():
    previous_year_prcp = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date.between(date_one_year_prev_most_recent, most_recent_date)).all()    
    
    return make_response(jsonify(dict(previous_year_prcp)))

@app.route('/api/v1.0/stations')
def station():
    stations = session.query(Station.station, Station.name).all()
    print(stations)
    return make_response(jsonify(dict(stations)))

@app.route('/api/v1.0/tobs')
def tobs():
    station_count = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).all()
    most_active_station = list(map(max, zip(*station_count))) 
    most_active_station_past_year_table = session.query(
        Measurement.date, Measurement.tobs).join(
        Station, Station.station == Measurement.station, isouter=True).filter(
        Measurement.station == most_active_station[0]).filter(
        Measurement.date.between(date_one_year_prev_most_recent, most_recent_date)).all()
    
    return make_response(jsonify(dict(most_active_station_past_year_table)))

@app.route('/api/v1.0/<start>')
def start_date(start):

    prcp_data = session.query(
        Measurement.date, func.tmin(Measurement.prcp)).all()

    return make_response(jsonify(dict(prcp_data)))


session.close()

if __name__ == "__main__":
    app.run(debug=True)