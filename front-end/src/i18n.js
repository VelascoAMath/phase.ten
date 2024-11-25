import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector'




i18next
.use(initReactI18next)
.use(LanguageDetector)
.init({
    fallbackLng: 'en',
    resources: {
        en: {
            translation: {
                notifications: 'Turn On Notifications',
                signUp: 'Sign Up',
                login: 'Log In',
                playGame: 'Play A Game',
                noConnection: 'Failed to establish connection',
                retryConnection: 'Retry connection',
                name: 'Name',
                userID: "User ID",
                token: "Token",
                confirmName: "Confirm Name",
                refresh: 'Refresh',
                logOut: 'Log Out',
                createGame: 'Create Game',
                deleteGame: 'Delete Game',
                edit: 'Edit',
                play: 'Play',
                start: 'Start',
                join: 'Join',
                unjoin: 'Unjoin',
                host: 'Host',
                editGame: 'Edit game',
                phaseList: 'Phase List',
                addPhase: 'Add Phase',
                removePhase: 'Remove Phase',
                changePhase: 'Change Phase',
                reset: 'Reset',
                gameType: 'Game Type',
                players: 'Players',
                currentPlayer: 'Current player',
                createdAt: 'Created At',
                updatedAt: 'Updated At',
                invalidGameId: "{{gameID}} is not a valid game id!",
                winner: 'Winner',
                deleteGameWarning: 'Are you sure you want to delete this game? It\'s already in progress',
                mustLogIn: "You must log in first!",
                noGamesMessage: "There seem to be no games. Why don't you create one?",
            }
        },
        es: {
            translation: {
                notifications: 'Prender Notificaciones',
                signUp: 'Registrar',
                login: 'Loguearse',
                playGame: 'Jugar Un Juego',
                noConnection: 'No hay conneccion',
                retryConnection: 'Tratar a connectar',
                name: 'Nombre',
                userID: "ID de la accuenta",
                token: "Token",
                confirmName: "Confirmar Nombre",
                refresh: 'Refrescar',
                logOut: 'Desloguearse',
                createGame: 'Crear Juego',
                deleteGame: 'Vorar Juego',
                edit: 'Editar',
                play: 'Jugar',
                start: 'Empezar',
                join: 'Juntar',
                unjoin: 'Salir',
                host: 'Organizador',
                editGame: 'Editar juego',
                phaseList: 'Lista De Fase',
                addPhase: 'Poner Fase',
                removePhase: 'Quitar Fase',
                changePhase: 'Cambiar Fase',
                reset: 'Resetear',
                gameType: 'Tipo de Juego',
                players: 'Jugadores',
                currentPlayer: 'Jugador Actual',
                createdAt: 'Creado En',
                updatedAt: 'Actualizado En',
                invalidGameId: "{{gameID}} no es un ID de juego valido!",
                winner: 'Ganador',
                deleteGameWarning: 'Estás seguro que quieres vorar este juego? Ya ha empezado',
                mustLogIn: "Se tiene que loguear!",
                noGamesMessage: "No hay juegos. ¿Por qué no creas uno?",
            }
        },
    }
})





