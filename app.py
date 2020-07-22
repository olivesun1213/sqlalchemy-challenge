import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


################################################
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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")

#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
def precipitation():
    session = Session(engine)

    # find date and prcp from measurement table
    results =   session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    # Convert the list to dictionary and then jsonify
    prcp_list = []

    for date, prcp in results:
        dict = {}
        dict[date] = prcp
        prcp_list.append(dict)

    session.close()

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.


def stations():
    session = Session(engine)

    stations = {}

    # Query all stations
    results = session.query(Station.station, Station.name).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.

def tobs():
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    date_1year_ago = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_1year_ago).all()
    
    tobs_list = []

    for date, tobs in results:
        dict = {}
        dict[date] = tobs
        tobs_list.append(dict)

    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def calc_temp(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    result_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        temp_range = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(temp_range)

    session.close()    

    return jsonify(result_list)

@app.route("/api/v1.0/<start>/<end>")
def calc_temp(start,end):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d

    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    result_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).filter(Measurement.date <= end_date).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        temp_range = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(temp_range)

    session.close()    

    return jsonify(result_list)


if __name__ == '__main__':
    app.run(debug=True)

