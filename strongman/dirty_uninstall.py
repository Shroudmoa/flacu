import shutil

import os





TIGW_DIR = "/home/vm/tigw"





def dirty_uninstall():



    if not os.path.exists(TIGW_DIR):

        return "/home/vm/tigw does not exist"





    try:



        shutil.rmtree(TIGW_DIR)



        return (

            "/home/vm/tigw deleted successfully\n"

            "Dirty uninstall completed"

        )





    except Exception as e:



        return f"Dirty uninstall failed: {str(e)}"
