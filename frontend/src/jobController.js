// import { commitMutation, graphql } from "react-relay";
// import environment from "./relayEnvironment";
//
// const getFileDownloadIdMutation = graphql`
//   mutation ResultFileMutation($input: GenerateFileDownloadIdsInput!) {
//     generateFileDownloadIds(input: $input) {
//       result
//     }
//   }
// `;
//
// const generateDownload = (url) => {
//   // Generate a file download link and click it to download the file
//   const link = document.createElement("a");
//   link.href = url;
//   link.target = "_blank";
//   document.body.appendChild(link);
//   link.click();
//   document.body.removeChild(link);
// };
//
// export const performFileDownload = (e, jobId, token) => {
//   e.preventDefault();
//   e.target.classList.add("link-visited");
//
//   commitMutation(environment, {
//     mutation: getFileDownloadIdMutation,
//     variables: {
//       input: {
//         jobId: jobId,
//         downloadTokens: [token],
//       },
//     },
//     onCompleted: (response, errors) => {
//       if (errors) {
//         // eslint-disable-next-line no-alert
//         alert("Unable to download file.");
//       } else {
//         generateDownload(
//           import.meta.env.VITE_JOB_CONTROLLER_URL +
//             response.generateFileDownloadIds.result[0]
//         );
//       }
//     },
//   });
// };
