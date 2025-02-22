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
        cls.leader_board.sort(key=lambda x: -x[0])

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

async def initialize_leaderboad():
    db = await get_database()
    users = await db.Users.find().to_list()
    LeaderBoard.initialize_leaderboard(users)