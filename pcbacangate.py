

# import the library
import can
import sys 

import lib4relind
import time

import sqlite3

import keyboard
import threading

import logging
import structlog


def process_data():
    # Replace this with your data processing code
    print("Processing data...")

def main():


# Valida que existan la base de datos, la tarjeta de relays y el modulo de can
# En caso de estar todo bien continua a main, en caso de error aborta y loggea diagnostico

    num_errors = 0
    log_ok = 0
    database_ok=0
    can_ok=0
    io_ok = 0
   
    try:

        print('Configuring Logging')
        # Configure the built-in logging module to write logs to a file
        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
            handlers=[
                logging.FileHandler("log.txt")  # Logging to a file named 'log.txt'
            ]
        )

        # Configure structlog to use the standard library's logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()  # or structlog.processors.KeyValueRenderer() for plain text logs
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Get a logger
        logger = structlog.get_logger()

        # Log some structured data
        logger.info("log_event", event_description="This is a initial log", value=1)

    except Exception as e:
        # This block will catch any exception
        num_errors+=1
        print(f"An error occurred: {e} while Verifing logging connection")
    else:
        # Code to execute if no exceptions were raised
        print("logging connection succesfuly tested")
        log_ok+=1
    finally:
        # Code that is always executed
        print("Continuing program")


# Valida que existan la base de datos, la tarjeta de relays y el modulo de can
# En caso de estar todo bien continua a main, en caso de error aborta y loggea diagnostico

    try:
        
        
        print('Verifing database connection')
        print('database version')
        print(sqlite3.sqlite_version)
        con = sqlite3.connect('pcba.db') 
        cur = con.cursor() 

        cur.execute("SELECT frame FROM frames WHERE id = 1")
        rows = cur.fetchall() 
        num_rows=0
        for row in rows:
            num_rows+=1
            print(row)
            hex_string = row[0]  # Extract the string from the tuple

            # Convert the string of hexadecimal numbers into an array
            byte_array = [int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2)]

            print(byte_array)

        con.close()
    except Exception as e:
            # This block will catch any exception
            num_errors+=1
            print(f"An error occurred: {e} while Verifing database connection")

            if (log_ok == 1):
                 logger.info("log_error", event_description="An error occurred: while Verifing database connection", value=e)
    else:
    # Code to execute if no exceptions were raised
        if (num_rows==1):

            print("Database connection succesfuly tested")
            database_ok+=1
            if (log_ok == 1):
                    logger.info("log_event", event_description="Database connection succesfuly tested", value=1)
        else:
            num_errors+=1             
            if (log_ok == 1):
                logger.info("log_error", event_description="An error occurred: while Verifing database connection", value=e)
    finally:
        # Code that is always executed
        print("Continuing program")


    try:
        print('Verifing io connection')

        lib4relind.set_relay(0,1,1)
        lib4relind.set_relay(0,2,1)
        lib4relind.set_relay(0,3,1)
        lib4relind.set_relay(0,4,1)
        time.sleep(3)
        lib4relind.set_relay(0,1,0)
        lib4relind.set_relay(0,2,0)
        lib4relind.set_relay(0,3,0)
        lib4relind.set_relay(0,4,0)

    except Exception as e:
            # This block will catch any exception
            num_errors+=1
            print(f"An error occurred: {e} while Verifing io connection")

            if (log_ok == 1):
                 logger.info("log_error", event_description="An error occurred: while Verifing io connection", value=e)
    else: 
    # Code to execute if no exceptions were raised
        print("IO connection succesfuly tested")
        io_ok+=1
        if (log_ok == 1):
                 logger.info("log_event", event_description="io connection succesfuly tested", value=1)
    finally:
        # Code that is always executed
        print("Continuing program")

    try:

        print('Verifing can bus card')
        # create a bus instance using 'with' statement,
        # this will cause bus.shutdown() to be called on the block exit;
        # many other interfaces are supported as well (see documentation)
        with can.Bus(interface='socketcan',
                    channel='can0',
                    receive_own_messages=True) as bus:

            # send a message
            message = can.Message(arbitration_id=100, is_extended_id=True,
                                    data=[0x11, 0x22, 0x33])
            bus.send(message, timeout=0.2)

            # iterate over received messages
            #for msg in bus:
            #    print(f"{msg.arbitration_id:X}: {msg.data}")

            # or use an asynchronous notifier
            #notifier = can.Notifier(bus, [can.Logger("recorded.log"), can.Printer()])

    except Exception as e:
                # This block will catch any exception
            num_errors+=1
            print(f"An error occurred: {e} while Verifing CAN connection")

            if (log_ok == 1):
                    logger.info("log_error", event_description="An error occurred: while Verifing CAN connection", value=e)
    else:
        # Code to execute if no exceptions were raised
            print("CAN connection succesfuly tested")
            can_ok+=1
            if (log_ok == 1):
                    logger.info("log_event", event_description="CAN connection succesfuly tested", value=1)
    finally:
            # Code that is always executed
            print("Continuing program")


    print("Press CTRL+C to stop...")

    #SI LLEGO AQUI EL EQUIPO ESTA LISTO
    #INICIA LOOP INFINITO

    def listen_for_exit_command():
        input("Press Enter to stop...\n")
        global keep_running
        
        
        keep_running = False

    keep_running = True
    exit_listener_thread = threading.Thread(target=listen_for_exit_command)
    exit_listener_thread.start()

    try:
        while (keep_running and num_errors == 0):
            # Your main loop code here
            print("Processing data...")
            time.sleep(0.1)  # Added for demonstration; replace with actual work

            # Declare byte_array outside the database connection scope
            byte_array = []
            
            # lee las señales de entrada, el codigo y el trigger
            inputs =lib4relind.get_opto_all(0)
            #testing id and trigger
            inputs = 3
            #inputs = 5
            #inputs = 7

             # Define the variable
            id = 0  # or any other value you want to query for
            trigger = 0

                
            id = inputs // 2
            trigger = inputs % 2
            if (id>0 and trigger >0):
                # cuando detecta el trigger
                # consulta la base de datos y enviar los datos por can
                # mientras este el trigger presente
                # regresa a leer las señales de entrada


                con = sqlite3.connect('pcba.db')
                cur = con.cursor()

                # Use a parameterized query
                cur.execute("SELECT frame FROM frames WHERE id = ?", (id,))
                rows = cur.fetchall()
                num_rows = 0
                for row in rows:
                    num_rows += 1
                    print(row)
                    hex_string = row[0]  # Extract the string from the tuple

                    # Convert the string of hexadecimal numbers into an array
                    byte_array = [int(hex_string[i:i+2], 16) for i in range(0, len(hex_string), 2)]

                    print(byte_array)

                    if (log_ok == 1):
                        logger.info("log_event", event_description="Sending Message", value=byte_array)
                con.close()

            # many other interfaces are supported as well (see documentation)
                with can.Bus(interface='socketcan',
                            channel='can0',
                            receive_own_messages=True) as bus:

                    # send a message
                    message = can.Message(arbitration_id=100, is_extended_id=True,
                                            data=byte_array)
                    bus.send(message, timeout=0.2)


        print("Stopping gracefully...")

    except KeyboardInterrupt:
        keep_running = False
        print("Program terminated via KeyboardInterrupt")
        if (log_ok == 1):
                    logger.info("log_event", event_description="Program terminated via KeyboardInterrupt", value=0)
    finally:
        if(num_errors>0) :
            print("Program terminated equipment not ready")
    # Wait for the exit command listener thread to finish
    exit_listener_thread.join()
    print("Program exited")







if __name__ == "__main__":
    main()




  


