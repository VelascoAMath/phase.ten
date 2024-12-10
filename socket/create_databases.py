from configparser import ConfigParser

import psycopg2


def create_databases():
    parser = ConfigParser()
    parser.read('database.ini')
    config = dict(parser.items('postgresql'))
    
    with psycopg2.connect(**config) as conn:
        cur = conn.cursor()
        
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS public.users (
                id uuid NOT NULL,
                "name" text NOT NULL,
                "token" text NOT NULL,
                is_bot boolean DEFAULT false NOT NULL,
                created_at timestamp NOT NULL,
                updated_at timestamp NOT NULL,
                CONSTRAINT users_pk PRIMARY KEY (id)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS users_name_isbot_idx ON public.users ("name",is_bot);
            CREATE INDEX IF NOT EXISTS users_name_idx ON public.users ("name");
            """
        )
        cur.execute("""
        do $$ BEGIN
            create type game_type as enum ('NORMAL', 'LEGACY', 'ADVANCEMENT');
        exception
            when duplicate_object then null;
        end $$;
        """)
        cur.execute("""
        
        CREATE TABLE IF NOT EXISTS public.games (
            id uuid NOT NULL,
            phase_list json NOT NULL,
            deck json NOT NULL,
            "discard" json NOT NULL,
            current_player uuid NOT NULL,
            host uuid NOT NULL,
            in_progress boolean DEFAULT false NOT NULL,
            type game_type DEFAULT 'NORMAL',
            winner uuid DEFAULT NULL NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL,
            CONSTRAINT games_pk PRIMARY KEY (id),
            CONSTRAINT games_users_fk FOREIGN KEY (current_player) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT games_users_fk_1 FOREIGN KEY (host) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT games_users_fk_2 FOREIGN KEY (winner) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.players (
            id uuid NOT NULL,
            game_id uuid NOT NULL,
            user_id uuid NOT NULL,
            hand json NOT NULL,
            turn_index serial NOT NULL,
            phase_index int NOT NULL,
            drew_card boolean DEFAULT false NOT NULL,
            completed_phase boolean DEFAULT false NOT NULL,
            skip_cards json NOT NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL,
            CONSTRAINT players_pk PRIMARY KEY (id),
            CONSTRAINT players_games_fk FOREIGN KEY (game_id) REFERENCES public.games(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT players_users_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        CREATE UNIQUE INDEX IF NOT EXISTS players_game_id_user_id_idx ON public.players (game_id,user_id);
        CREATE UNIQUE INDEX IF NOT EXISTS players_game_id_turn_index_idx ON public.players (game_id,turn_index);
    
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.gamephasedecks (
            id uuid NOT NULL,
            game_id uuid NOT NULL,
            phase text NOT NULL,
            deck json NOT NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL,
            CONSTRAINT gamephasedecks_pk PRIMARY KEY (id),
            CONSTRAINT gamephasedecks_games_fk FOREIGN KEY (game_id) REFERENCES public.games(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    
        """)
        
        cur.execute("""

        CREATE OR REPLACE VIEW public.players_with_names
        AS SELECT u.name,
            p.game_id,
            p.hand,
            p.turn_index,
            p.phase_index,
            p.skip_cards,
            p.drew_card,
            p.completed_phase,
            p.id
           FROM players p
             JOIN users u ON p.user_id = u.id
          ORDER BY p.game_id, p.turn_index;

        CREATE OR REPLACE VIEW public.completed_games AS select g.id, u."name" as "current player", g.phase_list, g.deck,
        g."discard", u2."name" as "host", g.in_progress, u3.name as "winner" from games g join users u on
        g.current_player =u.id join users u2 on u2.id = g.host join users u3 on g.winner = u3.id;


        CREATE OR REPLACE VIEW public.noncompleted_games AS select g.id, u."name" as "current player", g.phase_list, g.deck,
        g."discard", u2."name" as "host", g.in_progress, g.winner from games g join users u on g.current_player = u.id join
        users u2 on u2.id = g.host where g.winner is null;

        """)
        
        conn.commit()


def main():
    create_databases()


if __name__ == "__main__":
    main()
