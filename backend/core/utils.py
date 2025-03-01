# core/utils.py
import bisect

def serialize_document(doc):
    """Convert MongoDB document to a JSON-serializable format."""
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc


class LeaderBoard:
    leader_board = []

    @classmethod
    def initialize_leaderboard(cls, users):

        for user in users:
            cls.leader_board.append((user.get("coins"), user.get("user_id")))
        print(cls.leader_board)
        cls.leader_board.sort(key=lambda x: x[0])

    @classmethod
    def update(cls, user_id, score):

        for i, entry in enumerate(cls.leader_board):
            if entry[1] == user_id:
                cls.leader_board.pop(i)
                break
        new_entry = (score, user_id)
        bisect.insort_right(cls.leader_board, new_entry,key=lambda x: -x[0])
        # cls.leader_board.insert(index, new_entry)

    @classmethod
    def showLeaderboard(cls):
        return cls.leader_board

@classmethod
def initialize_leaderboard(cls, users):
    cls.leader_board = []
    
    for user in users:
        coins = user.get("coins")
        user_id = user.get("user_id")

        # Debugging print statements
        print(f"User: {user}, Coins: {coins}, User ID: {user_id}")

        # Ensure coins is a number, default to 0 if None or invalid
        if not isinstance(coins, (int, float)):
            print(f"Invalid coins value: {coins} for user {user_id}, setting to 0")
            coins = 0  

        cls.leader_board.append((coins, user_id))

    # Debugging: Print before sorting
    print("Before sorting:", cls.leader_board)

    try:
        cls.leader_board.sort(key=lambda x: x[0])
    except Exception as e:
        print("Sorting error:", e, "Leaderboard content:", cls.leader_board)
    
    print("After sorting:", cls.leader_board)

