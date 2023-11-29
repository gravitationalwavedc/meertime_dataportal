import { Container, Nav, Navbar } from "react-bootstrap";
import { Link, useRouter } from "found";

const TopNav = () => {
  const { router } = useRouter();

  const logout = () => {
    sessionStorage.clear();
    localStorage.clear();
    router.replace("/");
  };

  return (
    <Navbar bg="dark" variant="dark" className="mb-5" expand="md">
      <Container>
        <Link to="/" exact as={Navbar.Brand}>
          MEERTIME
        </Link>
        <Navbar.Toggle aria-controls="top-navbar" />
        <Navbar.Collapse id="top-navbar">
          <Nav className="mr-auto">
            <Link to="/" exact as={Nav.Link}>
              Folded
            </Link>
            <Link to="/search/" exact as={Nav.Link}>
              Search mode
            </Link>
            <Link to="/last-session/" exact as={Nav.Link}>
              Last session
            </Link>
            <Link to="/sessions/" exact as={Nav.Link}>
              Sessions
            </Link>
          </Nav>
          <Nav>
            <Link to="/token_generate/" exact as={Nav.Link}>
              Generate Token
            </Link>
            <Link to="/password_change/" exact as={Nav.Link}>
              Change Password
            </Link>
            <Nav.Link onClick={logout}>Log out</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default TopNav;
