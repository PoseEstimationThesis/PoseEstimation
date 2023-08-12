import logic.Camera as Camera
import visual.Interface as Interface



def main():
   basic_object = Camera.CameraObject(0)
   basic_object.start_capturing()
   Interface.BasicInterface.initialize_interface()

if __name__ == "__main__":
    main()
