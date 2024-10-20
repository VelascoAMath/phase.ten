import json
import sqlite3
import uuid

import psycopg2

VERBOSE = False


def add_db_functions(db_name, unique_indices=None, single_foreign=None, plural_foreign=None, serial_set=None):
    """
    This is a wrapper which will add postgresql-related functions to a class.
    In order to use this, a couple of things must be true
    1) Your class must have functions named to_json_dict() and from_json_dict().
    Essentially, you must have methods that can convert your objects into JSON objects and vice-versa.
    
    2) Your class must have an attribute named "id".
    As the name implies, this will represent the unique ID assigned to each object
    
    3) You must create the database first.
    This wrapper will not create them for you.
    
    
    4) You must call the class method set_cursor(cur) and set your cursor
    This cursor will be used to retrieve and set information from your database
    https://www.psycopg.org/docs/usage.html
    
    5) If you reference other objects, you must do so by their id, and their class definition must also have this wrapper.
    Do not have your class contain objects of other types.
    You must also specify if there is one or multiple objects associated with an id.
    Use the single_foreign and plural_foreign parameters to do so
    
    6) Columns that are a serial type (smallserial, serial, bigserial) should be specified through the serial_set
    parameter. This will prevent us from trying to save values to them and allow for new values to be automatically
    generated by postgresql
    
    7) The order of columns must match their counterparts' declaration in the class
    
    
    
    If requirements are obtained, you should be able to call these functions
    
    set_cursor(cur: psycopg2.extensions.cursor):
    This will set the cursor needed to access the postgresql database
    This should be the very first function called
    
    all():
    Get every object in the database
    
    exists(id: uuid|str) -> bool:
    Indicates if the object is in the database
    
    delete():
    Deletes the object's entry from the database
    
    save():
    Saves the object in the database
    
    get_by_id(id: uuid|str):
    Returns an object in the database with a specified id
    
    If you provided single foreign keys, you can also use these functions to obtain those objects
    
    get_x():
    Returns an object of type x where x is the type of object associated with the table.
    
    If you provided plural foreign keys, you can also use these functions to obtain those objects
    
    get_x():
    Returns a list of objects of type x where x is the type of object associated with the table.
    
    get_x_where():
    Not sure. I suspect that this function is currently broken
    
    
    :param serial_set: set of attributes in the class which correspond to serial types in the database
    :param plural_foreign:
    :param single_foreign:
    :param db_name: the name of the database used my postgres. Because this will be put directly into SQL commmands,
    we will not check for SQL injections. It is up to the user to pass in a valid database name
    :param unique_indices: a list of lists of indexes in the database which are require to be UNIQUE
    :return:
    """
    
    if serial_set is None:
        serial_set = set()
    if plural_foreign is None:
        plural_foreign = set()
    if single_foreign is None:
        single_foreign = set()
    if unique_indices is None:
        unique_indices = set()
    
    def decorator(cls):
        if "id" not in cls.__annotations__:
            raise Exception(f"{cls} does not have an id attribute!")
        
        # Get a list of variables in the class
        var_list = list(cls.__annotations__.keys())
        # Of course, we don't need the cursor for our database operations
        if 'cur' in var_list:
            var_list.remove('cur')
        if VERBOSE:
            print(var_list)
        
        @staticmethod
        def from_sql_tuple(sql_row):
            json_dict = {}
            for i, key in enumerate(var_list):
                json_dict[key] = sql_row[i]
            
            return cls.from_json_dict(json_dict)
        
        @staticmethod
        def set_cursor(cur: sqlite3.Cursor | psycopg2.extensions.cursor):
            if isinstance(cur, sqlite3.Cursor) or isinstance(cur, psycopg2.extensions.cursor):
                cls.cur = cur
            else:
                raise Exception(f"Unrecognized type {type(cur)} for a database cursor!")
        
        cls.set_cursor = set_cursor
        
        @staticmethod
        def all():
            cls.cur.execute(f"SELECT * FROM {db_name}")
            
            result = []
            for sql_line in cls.cur.fetchall():
                result.append(from_sql_tuple(sql_line))
            
            return result
        
        @staticmethod
        def exists(id: str | uuid.UUID) -> bool:
            if isinstance(id, uuid.UUID):
                id = str(id)
            
            cls.cur.execute(f"SELECT * FROM {db_name} WHERE id=%s", (id,))
            return cls.cur.fetchone() is not None
        
        def delete(self):
            if exists(self.id):
                if VERBOSE:
                    print(cls.cur.mogrify(f"DELETE FROM {db_name} WHERE id = %s", (str(self.id),)))
                cls.cur.execute(f"DELETE FROM {db_name} WHERE id = %s", (str(self.id),))
        
        def save(self):
            x = self.to_json_dict()
            
            if exists(self.id):
                # (name1, name2 item3, ...)
                set_list = []
                # The actual values that will go in the final tuple
                attr_list = []
                for (key, val) in x.items():
                    if key == "id":
                        continue
                    if val is None:
                        continue
                    if key in serial_set:
                        continue
                    set_list.append(f"{key}=%s")
                    
                    if isinstance(val, str):
                        attr_list.append(val)
                    else:
                        attr_list.append(json.dumps(val))
                
                attr_list.append(str(self.id))
                command = f"UPDATE {db_name} SET " + ','.join(set_list) + f" WHERE id=%s;"
                cls.cur.execute(command, tuple(attr_list))
            else:
                # (name1, name2 item3, ...)
                set_list = []
                # The actual values that will go in the final tuple
                attr_list = []
                
                for (key, val) in x.items():
                    # psycopg2 doesn't properly turn None into NULL
                    if val is None:
                        continue
                    if key in serial_set:
                        continue
                    
                    set_list.append(key)
                    
                    if key == "id":
                        attr_list.append(str(val))
                    elif isinstance(val, str):
                        attr_list.append(val)
                    else:
                        attr_list.append(json.dumps(val))
                
                question_tuple = ",".join(["%s" for _ in attr_list])
                command = f"INSERT INTO {db_name} (" + ','.join(set_list) + f") VALUES ({question_tuple});"
                if VERBOSE:
                    print(cls.cur.mogrify(command, tuple(attr_list)))
                cls.cur.execute(command, tuple(attr_list))
        
        @staticmethod
        def get_by_id(id: str | uuid.UUID):
            if isinstance(id, uuid.UUID):
                id = str(id)
            
            cls.cur.execute(f"SELECT * FROM {db_name} WHERE id=%s", (id,))
            
            sql_tuple = cls.cur.fetchone()
            if sql_tuple is None:
                raise Exception(cls.cur.mogrify(f"SELECT * FROM {db_name} WHERE id=%s", (id,)))
            return from_sql_tuple(sql_tuple)
        
        cls._db_name = db_name
        cls.all = all
        cls.exists = exists
        cls.save = save
        cls.delete = delete
        cls.get_by_id = get_by_id
        cls.from_sql_tuple = from_sql_tuple
        
        for unique_index in unique_indices:
            key = f"get_by_{'_'.join(unique_index)}"
            
            def get_by(*args):
                if len(args) != len(unique_index):
                    raise Exception(f"{key} takes exactly {len(unique_index)} argument ({len(args)} given)!")
                
                converted_args = [str(arg) for arg in args]
                
                where_clause = ' AND '.join([f"{index}=%s" for index in unique_index])
                
                command = f"SELECT * FROM {db_name} WHERE {where_clause} LIMIT 1"
                cls.cur.execute(command, converted_args)
                
                return from_sql_tuple(cls.cur.fetchone())
            
            def exists_by(*args):
                if len(args) != len(unique_index):
                    raise Exception(
                        f"exists_by_{'_'.join(unique_index)} takes exactly {len(unique_index)} argument ({len(args)} given)!")
                
                converted_args = [str(arg) for arg in args]
                
                where_clause = ' AND '.join([f"{index}=%s" for index in unique_index])
                
                command = f"SELECT * FROM {db_name} WHERE {where_clause} LIMIT 1"
                cls.cur.execute(command, converted_args)
                
                return cls.cur.fetchone() is not None
            
            setattr(cls, key, get_by)
            setattr(cls, f"exists_by_{'_'.join(unique_index)}", exists_by)
        
        # Defines the get_item functions for the class
        for (key_name, other_cls) in single_foreign:
            def get_item_by_name(key_name):
                def get_item(self):
                    command = f"SELECT {other_cls._db_name}.* FROM {db_name} JOIN {other_cls._db_name} ON {db_name}.{key_name}_id = {other_cls._db_name}.id WHERE {db_name}.id = %s"
                    
                    cls.cur.execute(command, (str(self.id),))
                    return other_cls.from_sql_tuple(cls.cur.fetchone())
                
                return get_item
            
            setattr(cls, f"get_by_{key_name}", get_item_by_name(key_name))
        
        for (key_name, item_name, other_cls) in plural_foreign:
            def get_items_by_name(key_name:str, other_cls):
                
                def get_item(id):
                    command = f"SELECT distinct on ({other_cls._db_name}.id) {other_cls._db_name}.* FROM {db_name} JOIN {other_cls._db_name} ON {db_name}.{key_name} = {other_cls._db_name}.id WHERE {other_cls._db_name}.id = %s;"
                    if VERBOSE:
                        print(cls.cur.mogrify(command, (str(id),)))
                    cls.cur.execute(command, (str(id),))
                    return other_cls.from_sql_tuple(cls.cur.fetchone())
                
                return get_item
            
            # I think this may be broken
            def get_items_using_where(key_name:str, other_cls):
                def get_items(id):
                    if isinstance(id, uuid.UUID):
                        id = str(id)
                    command = f"SELECT * FROM {db_name} WHERE {key_name} = %s"
                    cls.cur.execute(command, (id,))
                    if VERBOSE:
                        print(cls.cur.mogrify(command, (id,)))
                    return [cls.from_sql_tuple(sql_tuple) for sql_tuple in cls.cur.fetchall()]
                
                return get_items
            
            setattr(cls, f"get_{item_name}", get_items_by_name(key_name, other_cls))
            setattr(cls, f"all_where_{key_name}", get_items_using_where(key_name, other_cls))
        
        return cls
    
    return decorator
