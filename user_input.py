# user_input.py
import threading
from time import sleep
from hex_extractor import HexExtractor
from instruction import Instruction
# from interpreter import Interpreter
from debuger import Debug
import queue

debugger = Debug()

def debug(self, *args, **kwargs):
    debugger.debug(*args, **kwargs)
    # await_go_command_thread = threading.Thread(target=console_input)
    # input_thread.start()

    # def get_user_input(self):
    #     if not self.user_input_queue.empty():
    #         user_input = self.user_input_queue.get(False)
    #         return user_input

class UserInput:
    def __init__(self, user_input_queue):
        self.user_input_queue = user_input_queue
        self.should_read_input = False

        # self.should_read_input = self.await_initial_start_command()

    # def await_initial_start_command(self):
    #     # Create an event to signal when input is received
    #     input_event = threading.Event()

    #     # Function to get user input from the console
    #     # def console_input():
    #     #     user_input = input("Enter something: ")
    #     #     input_event.set()
    #     #     return user_input

    #     # # Start a thread to wait for console input
    #     # input_thread = threading.Thread(target=console_input)
    #     # input_thread.start()

    #     # Wait for either queue to have an item or user input
    #     while True:
    #         if not self.user_input_queue.empty():
    #             coppied_queue = self.user_input_queue.queue
    #             if coppied_queue.get() == "BEGIN_READING_USER_INPUT":
    #                 return True
    #             else:
    #                 continue
    #         # if input_event.is_set():
    #         #     return True


    def get_user_input(self):
        # Create an event to signal when input is received
        input_event = threading.Event()

        # # Function to get user input from the console
        # def console_input():
        #     user_input = input("Enter something: ")
        #     input_event.set()
        #     return user_input

        # # Start a thread to wait for console input
        # input_thread = threading.Thread(target=console_input)
        # input_thread.start()

        # Wait for either queue to have an item or user input
        while True:
            sleep(.1)
            if not self.user_input_queue.empty():
                if self.should_read_input:
                    coppied_queue = self.user_input_queue.queue
                    print(f"{coppied_queue} recieved from GUI")
                    if coppied_queue[0] == "END_READING_USER_INPUT":
                        throwaway_input = self.user_input_queue.get()
                        print(f"threw away the input: {throwaway_input}")
                        self.should_read_input = False
                        continue
                    return self.user_input_queue.get(False)
                else:
                    coppied_queue = self.user_input_queue.queue
                    print(f"{coppied_queue} recieved from GUI")
                    if coppied_queue[0] == "BEGIN_READING_USER_INPUT":
                        throwaway_input = self.user_input_queue.get()
                        print(f"threw away the input: {throwaway_input}")
                        self.should_read_input = True
                        # input_thread.join()

                        # throwaway_input = self.user_input_queue.get(False)
                        # final_input = self.user_input_queue.get(False)
                        # print(throwaway_input)
                        # print(final_input)
                        # return self.user_input_queue.get(False)
                    else:
                        continue
            # if input_event.is_set():
            #     return self.user_input_queue.get(False)
            # sleep(0.5)

# class UserInput:
#     def __init__(self, user_input_queue):
#         self.user_input_queue = user_input_queue
#         self.stop_event = threading.Event()
#         self.user_input = ""

#     def get_user_input(self):
#         input_event = threading.Event()
#         result = [None]  # Use a list to store the result

#         def console_input():
#             # sleep(12)
#             try:
#                 user_input = input("Enter something: ")
#                 # self.user_input_queue.put(user_input)
#                 self.user_input = user_input
#                 input_event.set()
#             except EOFError:
#                 # Handle EOF (e.g., when input is closed)
#                 pass

#         input_thread = threading.Thread(target=console_input)
#         input_thread.daemon = False  # Set as daemon thread
#         input_thread.start()
#         for thread in threading.enumerate():
#             if thread.daemon or thread is threading.current_thread():
#                 print(f"user input thread: {thread}")
#                 continue
#             # thread.join()


#         return "user input"
#         # while not self.stop_event.is_set():
#         #     try:
#         #         if not self.user_input_queue.empty():
#         #             result[0] = self.user_input_queue.get_nowait()
#         #             break
#         #         if input_event.is_set():
#         #             result[0] = self.user_input
#         #             break
#         #     except queue.Empty:
#         #         pass

#         # return result[0]

#     def stop(self):
#         self.stop_event.set()