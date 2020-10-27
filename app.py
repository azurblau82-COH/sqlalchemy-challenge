import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start>/<end></br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query all the precip data from the past year
    Precip = session.query(Measurement.date, func.max(Measurement.prcp)).\
    filter(Measurement.date >= '2016-08-23').\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()

    session.close()

    # Create dataframe, then dictionary wth Date set as key and prcp as value
    Precip_df = pd.DataFrame(Precip, columns=['Date', 'Precipitation'])
    Precip_dict = Precip_df.set_index('Date').to_dict()  

    return jsonify(Precip_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query all station info
    stations = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create a dictionary     
    Station_df = pd.DataFrame(stations, columns=['Station', 'Name', 'Lat', 'Lng', 'Elev'])
    Station_dict = Station_df.set_index('Station').to_dict('index')

    return jsonify(Station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Temp from most active station
    Temp = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281', Measurement.date >='2016-08-23').all()
    
    session.close()

    # Create a dictionary
    Temp_df = pd.DataFrame(Temp, columns=['Date', 'Temp'])
    Temp_dict = Temp_df.set_index('Date').to_dict()

    return jsonify(Temp_dict)


@app.route("/api/v1.0/<start>")
def start_temp(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query stats, use 'start' input as filter for date
    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    

    session.close()

    # Create a dictionary
    date_range = f"{start} - 2017-08-23"
    stats_dict = {date_range:[{'Min': stats[0][0], 'Avg': stats[0][1], 'Max': stats[0][2]}]}
    return jsonify(stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_stop_temp(start, end):
    
    session = Session(engine)

    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    
    session.close()
    date_range = f"{start} - {end}"
    stats_dict = {date_range:[{'Min': stats[0][0], 'Avg': stats[0][1], 'Max': stats[0][2]}]}

    return jsonify(stats_dict)

if __name__ == '__main__':
    app.run(debug=True)