from pathlib import Path

def find_hispeed_dirs(datapath):
    return [f for f in Path(datapath).rglob("*hispeed*") if f.is_dir()]
def find_avi(datapath):
    return [f for f in Path(datapath).rglob("*.avi")]
def simplify(files):
    cnt = 0
    for f in files:
        simple_name = f.name.split("_")[-1]
        if simple_name != f.name:
            simple_name_path = f.parent.joinpath(simple_name)
            if not simple_name_path.exists():
                f.rename(simple_name_path)
            else:
                print('Path already exists: ', simple_name_path)

if __name__ == "__main__":
    hispeed_dirs = find_hispeed_dirs(r"Z:\Ariel\datasets\behavior_whisker_data_test")
    for hispeed in hispeed_dirs:
        avis = find_avi(hispeed)
        simplify(avis)