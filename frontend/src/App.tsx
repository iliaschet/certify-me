import { CertificateList } from './components/CertificateList'
import { SnackbarProvider } from 'notistack';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import CssBaseline from '@mui/material/CssBaseline';

function App() {

  return (
    <SnackbarProvider maxSnack={3}>
        <>
          <CssBaseline />
          <AppBar position="static" color="transparent">
            <Toolbar>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                Certify Me
              </Typography>
            </Toolbar>
          </AppBar>
          <CertificateList />
        </>
    </SnackbarProvider>
  );
}

export default App;
