import numpy as np
from database.database import get_connection

class MatrixFactorization:
    def __init__(self, R, K, alpha, beta, iterations):
        self.R = R
        self.num_users, self.num_items = R.shape
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iterations = iterations

    def train(self):
        self.P = np.random.normal(scale=1./self.K, size=(self.num_users, self.K))
        self.Q = np.random.normal(scale=1./self.K, size=(self.num_items, self.K))
        for i in range(self.iterations):
            self.sgd()
            if i % 10 == 0:
                print(f"Iteration {i}")

    def sgd(self):
        xs, ys = self.R.nonzero()
        for x, y in zip(xs, ys):
            e = self.R[x, y] - self.predict(x, y)
            self.P[x, :] += self.alpha * (e * self.Q[y, :] - self.beta * self.P[x, :])
            self.Q[y, :] += self.alpha * (e * self.P[x, :] - self.beta * self.Q[y, :])

    def predict(self, x, y):
        return self.P[x, :].dot(self.Q[y, :].T)

    def full_matrix(self):
        return np.dot(self.P, self.Q.T)

    def update_user_vector(self, user_id, interacted_product_ids, user_to_idx, product_to_idx, learning_rate=0.01):
        u_idx = user_to_idx.get(user_id)
        if u_idx is None:
            return

        for product_id in interacted_product_ids:
            i_idx = product_to_idx.get(product_id)
            if i_idx is None:
                continue

            prediction = np.dot(self.P[u_idx], self.Q[i_idx])
            error = 1.0 - prediction
            self.P[u_idx] += learning_rate * (error * self.Q[i_idx] - self.alpha * self.P[u_idx])

        # Save updated vector to DB
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_factors (user_id, factors)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE SET factors = EXCLUDED.factors
        """, (user_id, list(map(float, self.P[u_idx]))))
        conn.commit()
        cur.close()
        conn.close()

    def save_factors_to_db(self, user_to_idx, product_to_idx):
        conn = get_connection()
        cur = conn.cursor()

        for user_id, u_idx in user_to_idx.items():
            cur.execute("""
                INSERT INTO user_factors (user_id, factors)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET factors = EXCLUDED.factors
            """, (user_id, list(map(float, self.P[u_idx]))))

        for product_id, i_idx in product_to_idx.items():
            cur.execute("""
                INSERT INTO item_factors (product_id, factors)
                VALUES (%s, %s)
                ON CONFLICT (product_id) DO UPDATE SET factors = EXCLUDED.factors
            """, (product_id, list(map(float, self.Q[i_idx]))))

        conn.commit()
        cur.close()
        conn.close()

    def load_factors_from_db(self, user_to_idx, product_to_idx):
        conn = get_connection()
        cur = conn.cursor()

        self.P = np.zeros((len(user_to_idx), self.K))
        self.Q = np.zeros((len(product_to_idx), self.K))

        cur.execute("SELECT user_id, factors FROM user_factors")
        for user_id, factors in cur.fetchall():
            if user_id in user_to_idx:
                self.P[user_to_idx[user_id]] = factors

        cur.execute("SELECT product_id, factors FROM item_factors")
        for product_id, factors in cur.fetchall():
            if product_id in product_to_idx:
                self.Q[product_to_idx[product_id]] = factors

        cur.close()
        conn.close()