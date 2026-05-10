from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    # This allows us to access user.maps easily
    maps = relationship("MindMap", back_populates="owner")

class MindMap(Base):
    __tablename__ = "mind_maps"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    graph_json = Column(Text)  # Stores the nodes and links as a string
    user_id = Column(Integer, ForeignKey("users.id")) # Links to the user
    
    owner = relationship("User", back_populates="maps")
