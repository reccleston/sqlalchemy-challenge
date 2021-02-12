from flask import Flask, jsonify, make_response
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from scipy import stats as sts

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
    return make_response(jsonify({'available_links': ['/api/v1.0/precipitation', '/api/v1.0/stations', '/api/v1.0/tobs', '/api/v1.0/<start>', '/api/v1.0/<start>/<end>']}))

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
        Measurement.date, Measurement.prcp).filter(
        Measurement.date >= start).all()

    prcp = [days_prcp[1] for days_prcp in prcp_data if days_prcp[1]]

    tmin = sts.tmin(prcp)
    tmax = sts.tmax(prcp)
    # tavg = sts.tavg(prcp)

    return make_response(jsonify({start: {'tmin': tmin, 'tmax': tmax}}))

@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
    start_digits = start.split('-')
    end_digits = end.split('-')

    start = dt.datetime(int(start_digits[0]), int(start_digits[1]), int(start_digits[2]))
    end = dt.datetime(int(end_digits[0]), int(end_digits[1]), int(end_digits[2]))

    print(start, end)

    prcp_data = session.query(
        Measurement.date, Measurement.prcp).filter(
        Measurement.date.between(start, end)).all()

    prcp = [days_prcp[1] for days_prcp in prcp_data if days_prcp[1]]

    tmin = sts.tmin(prcp)
    tmax = sts.tmax(prcp)
    # tavg = sts.tavg(prcp)

    return make_response(jsonify({f'{start} to {end}': {'tmin': tmin, 'tmax': tmax}}))

session.close()

if __name__ == "__main__":
    app.run(debug=True)