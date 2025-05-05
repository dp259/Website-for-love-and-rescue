from sqlalchemy import create_engine, Integer, String, Float, MetaData, ForeignKey, Enum, Boolean, delete
from sqlalchemy.orm import DeclarativeBase, relationship, registry, Mapped, mapped_column, sessionmaker
import pandas as pd

engine = create_engine('sqlite:///joyandlove_db.db')
sex_enum = Enum('Male', 'Female', name='sex_enum')
ym_enum = Enum('year', 'month', name = 'ym_enum')
metadata = MetaData()

type_annotation_map = {
    str: String().with_variant(String(255), "mysql", "mariadb"),
    int: Integer,
    float: Float,
    bool: Boolean,
}
mapper_registry = registry(type_annotation_map = type_annotation_map)

class Base(DeclarativeBase):
    metadata = metadata 
    type_annotation_map = type_annotation_map
    mapper_registry = mapper_registry

class Dogs(Base):
    __tablename__ = 'Dogs'
    dog_id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    age: Mapped[int] = mapped_column(Integer, nullable = False)
    story: Mapped[str] = mapped_column(String(1000), nullable = False)
    sex: Mapped[str] = mapped_column(sex_enum, nullable = False)
    age_desc: Mapped[str] = mapped_column(ym_enum, nullable = False)
    adopted: Mapped[bool] = mapped_column(Boolean, default = False, nullable = False)
    fee: Mapped[float] = mapped_column(Float, nullable = False)

    race = relationship('Raza', back_populates = 'breed_tracker')
    descriptor = relationship('character', back_populates = 'characteristic_tracker')
    image = relationship('dog_image', back_populates = 'image_tracker')

class Raza(Base):
    __tablename__ = 'Raza'
    breed_id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    dog_id: Mapped[int] = mapped_column(Integer, ForeignKey('Dogs.dog_id'), nullable = False)
    breed: Mapped[str] = mapped_column(String(255), nullable = False)

    breed_tracker = relationship('Dogs', back_populates = 'race')

class character(Base):
    __tablename__ = 'character'
    characteristic_id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    dog_id: Mapped[int] = mapped_column(Integer, ForeignKey('Dogs.dog_id'), nullable = False)
    characteristic: Mapped[str] = mapped_column(String(255), nullable = False)

    characteristic_tracker = relationship('Dogs', back_populates = 'descriptor')
    
class dog_image(Base):
    __tablename__ = 'dog_image'
    image_id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    dog_id: Mapped[int] = mapped_column(Integer, ForeignKey('Dogs.dog_id'), nullable = False)
    img: Mapped[str] = mapped_column(String(255), nullable = False)

    image_tracker = relationship('Dogs', back_populates = 'image')

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind = engine)

#This is to delete the values in the tables for now until my datasets are complete!
#with Session() as session:
    #session.execute(delete(Dogs))
    #session.execute(delete(Raza))
    #session.execute(delete(character))
    #session.commit()

try:
    # Load the datasets
    df_dogs = pd.read_csv('Database\joyandlove_dog_info.csv', encoding='windows-1252')

    # Select important columns from dataset
    required_columns = ['name', 'age', 'breed', 'story', 'Sex', 'characteristic', 'age_desc', 'adopted', 'fee', 'image_paths']
    df_dogs = df_dogs[required_columns]

    df_dogs['story'] = df_dogs['story'].replace('?', 'Not yet known')
    df_dogs['story'] = df_dogs['story'].replace(':', ',')
    df_dogs['characteristic'] = df_dogs['characteristic'].replace('?', 'Not yet known')

    df_dogs['age'] = pd.to_numeric(df_dogs['age'], errors='coerce').fillna(0).astype(int)

    #Add datasets to respective table
    dogs = [
        Dogs(name = row['name'], age = row['age'], story = row['story'],
            sex = row['Sex'], age_desc = row['age_desc'], adopted = row['adopted'], fee = row['fee'])
        for _, row in df_dogs.iterrows()
    ]

    with Session() as session:
        session.bulk_save_objects(dogs)
        session.commit()

    breeds = []
    characteristics = []
    img_paths = []
    with Session() as session:
        dog_ids = {dog.name: dog.dog_id for dog in session.query(Dogs).all()}

        for _, row in df_dogs.iterrows():
            try:
                dog_id = dog_ids[row['name']]
                breed_list = row['breed'].split(':')
                for breed in breed_list:
                    breeds.append(Raza(dog_id = dog_id, breed = breed.strip()))
                
                characteristic_list = row['characteristic'].split(':')
                for char in characteristic_list:
                    characteristics.append(character(dog_id = dog_id, characteristic = char.strip()))

                img_list = row['image_paths'].split(':')
                for imagen in img_list:
                    img_paths.append(dog_image(dog_id = dog_id, img = imagen.strip()))
                
            except KeyError as e:
                print(f"Error processing row for dog '{row['name']}': {e}")

        session.bulk_save_objects(breeds)
        session.bulk_save_objects(characteristics)
        session.bulk_save_objects(img_paths)
        session.commit()

except Exception as e:
    print(f"Error, {e}, was encountered")
""""
with Session() as session:
    # Query all dogs
    all_dogs = session.query(Dogs).all()

    # Print each dog's name and age
    for dog in all_dogs:
        breeds = session.query(Raza).filter_by(dog_id = dog.dog_id).all()
        img_path = session.query(dog_image).filter(dog_image.dog_id == dog.dog_id).all()
        print(f"Name: {dog.name}, Age: {dog.age} {dog.age_desc}s, Adopted: {'Taken' if dog.adopted else 'Available'}")
        print("Breeds:")
        for breed in breeds:
            print(f"{breed.breed} breed")

        for img in img_path:
            print(f"{img.img}.jpg pathway")
            """