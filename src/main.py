import logic.Camera as Camera
import visual.Interface as Intefrace



def main():
   basic_object = Camera.CameraObject(0)
   basic_object.start_capturing()
   basic_object_interface = Intefrace.BasicInterface()
   basic_object_interface.initialize_interface()

if __name__ == "__main__":
    main()
