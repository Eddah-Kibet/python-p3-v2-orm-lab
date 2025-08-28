from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Table name (avoid mismatches!)
    table_name = "reviews"

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    # -------------------
    # Validations
    # -------------------
    @property
    def year(self):
        return self._year
    @year.setter
    def year(self, year):
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError("year must be greater than 1999")

    @property
    def summary(self):
        return self._summary
    @summary.setter
    def summary(self, summary):
        if isinstance(summary, str) and len(summary):
            self._summary = summary
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id
    @employee_id.setter
    def employee_id(self, employee_id):
        if employee_id in Employee.all.keys():
            self._employee_id = employee_id
        else:
            raise ValueError("the id is not present in employees table")

    # -------------------
    # Database methods
    # -------------------
    @classmethod
    def create_table(cls):
        sql = f"""
            CREATE TABLE IF NOT EXISTS {cls.table_name} (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employee(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = f"DROP TABLE IF EXISTS {cls.table_name};"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        sql = f"""
            INSERT INTO {self.table_name} (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review = cls.all.get(row[0])

        if review:
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3])
            review.id = row[0]
            cls.all[review.id] = review

        return review

    @classmethod
    def find_by_id(cls, id):
        sql = f"SELECT * FROM {cls.table_name} WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        sql = f"""
            UPDATE {self.table_name}
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        sql = f"DELETE FROM {self.table_name} WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        del type(self).all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        sql = f"SELECT * FROM {cls.table_name}"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
