import { Box, Typography } from "@mui/material";

const Homepage: React.FC = () => {

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      height="100vh"
    >
    <Typography variant="h1" gutterBottom>
    PLNK
    </Typography>
    <Typography variant="h2" gutterBottom>
        Quantitative microfund.
    </Typography>
    <Typography variant="h3" gutterBottom padding={3}>
        Averaged return p.a: 32%
    </Typography>
    </Box>
  );
};

export default Homepage;
