import time

class Timer:
    def __init__(self, minutes):
        self.minutes = minutes
        self.seconds = minutes * 60
        self.running = False
    
    def start(self):
        self.start_time = time.time()
        self.running = True
        while self.running:
            self.seconds = int(self.minutes * 60 - (time.time() - self.start_time))
            if self.seconds <= 0:
                print('Timer Selesai!')
                self.running = False
            else:
                mins, secs = divmod(self.seconds, 60)
                timeformat = '{:02d}:{:02d}'.format(mins, secs)
                print(timeformat, end='\r')
                time.sleep(1)
                
    def getStatus(self):
        return self.running
    
    def stop(self):
        self.running = False

    def restart(self):
        self.start()
        
    def reset(self):
        self.seconds = self.minutes * 60


