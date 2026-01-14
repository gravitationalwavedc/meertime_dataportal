import { graphql, usePreloadedQuery } from "react-relay";
import TemplateModal from "./TemplateModal";

export const templateQuery = graphql`
  query TemplateQuery($jname: String, $mainProject: String) {
    pulsarFoldResult(pulsar: $jname, mainProject: $mainProject) {
      foldingTemplate {
        id
        band
        templateFile
        createdAt
        project {
          short
        }
      }
      foldingTemplateIsEmbargoed
      foldingTemplateExistsButInaccessible
    }
  }
`;

const Template = ({ show, setShow, queryRef }) => {
  const data = usePreloadedQuery(templateQuery, queryRef);

  return <TemplateModal show={show} setShow={setShow} data={data} />;
};

export default Template;
