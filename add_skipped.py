import HNAPI
from HNAPI import HNFollower
import BayesModel

    
def main():
    f = HNAPI.create_follower()
    f.skipped = {}
    HNAPI.save_follower(f)

if __name__ == "__main__":
    main()
