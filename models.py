def create_valentine(conn, valentine_id, message, image_filenames):
    """Store a new valentine in the database"""
    cursor = conn.cursor()
    
    # Insert valentine
    cursor.execute(
        'INSERT INTO valentines (id, message) VALUES (?, ?)',
        (valentine_id, message)
    )
    
    # Insert images
    for filename in image_filenames:
        cursor.execute(
            'INSERT INTO images (valentine_id, filename) VALUES (?, ?)',
            (valentine_id, filename)
        )
    
    return valentine_id

def get_valentine(conn, valentine_id):
    """Retrieve a valentine and its images"""
    cursor = conn.cursor()
    
    # Get valentine
    cursor.execute(
        'SELECT * FROM valentines WHERE id = ?',
        (valentine_id,)
    )
    valentine = cursor.fetchone()
    
    if not valentine:
        return None
    
    # Get images
    cursor.execute(
        'SELECT * FROM images WHERE valentine_id = ? ORDER BY created_at',
        (valentine_id,)
    )
    images = cursor.fetchall()
    
    return valentine, images