import logging
import os
import sqlite3
from sqlite3 import Error


def create_connection():
    database = 'out/tip_bot.db'

    try:
        os.makedirs( os.path.dirname( database ), exist_ok = True )
        connection = sqlite3.connect( database )
        logging.info( 'Connected to the database.' )
        logging.debug( f'Db: ´{database}´' )

        return connection
    except Error as e:
        logging.error( e )

    return None


def close_connection( connection ):
    try:
        if connection:
            connection.close()
    except Error as e:
        logging.error( e )


def init_database( connection ):
    try:
        for statement in open( 'resources/schema.sql' ).read().split( '\n\n' ):
            connection.execute( statement )
            logging.debug( f'Table created:\n{statement}' )

        logging.info( 'Database tables ready.' )
    except Error as e:
        logging.error( e )


def execute_query( connection, query, parameters = None ):
    logging.debug( f'SQL: {query}. With parameters: ´{parameters}´' )
    try:
        cursor = connection.cursor()
        cursor.execute( query, parameters )
        logging.info( 'Query execution successful.' )

        return cursor.lastrowid
    except Error as e:
        logging.error( e )


def fetch_result( connection, query, parameters = None ):
    try:
        cursor = connection.cursor()

        if parameters is None:
            cursor.execute( query )
        else:
            cursor.execute( query, parameters )

        result = cursor.fetchall()
        logging.debug( f'Fetch result: {result}' )

        if len( result ) == 1:
            if len( result[ 0 ] ) == 1:
                return result[ 0 ][ 0 ]
            return result[ 0 ]
        elif len( result ) > 1:
            return result

        return None

    except Error as e:
        logging.error( e )
